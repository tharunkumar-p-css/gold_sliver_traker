"""
scheduler/tasks.py
==================
APScheduler background job — runs every 60 seconds.

Workflow per tick:
  1. Fetch latest gold + silver prices (via rates.services)
  2. For each active UserAlert, check if the % threshold is hit
  3. Send email / Telegram / both based on user preference
  4. Log to NotificationHistory
"""
import logging
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings

logger = logging.getLogger(__name__)
_scheduler = None


def check_alerts():
    """Core job: fetch prices → evaluate alerts → dispatch notifications."""
    from rates.services import fetch_and_save_rates, get_latest_rate
    from core.models import UserAlert
    from notifications.models import NotificationHistory
    from notifications.email_service import send_alert_email
    from notifications.sms_service import send_alert_sms, send_alert_whatsapp
    from notifications.telegram_service import send_alert_telegram

    logger.info("⏱  Scheduler tick: fetching prices …")
    try:
        rates = fetch_and_save_rates()
    except Exception as e:
        logger.error(f"Price fetch failed: {e}")
        return

    active_alerts = UserAlert.objects.filter(is_active=True).select_related(
        'user', 'user__profile'
    )

    for alert in active_alerts:
        rate_obj = rates.get(alert.metal)
        if not rate_obj:
            continue

        current_price = float(rate_obj.price_usd)
        base_price = float(alert.base_price)

        pct_change = ((current_price - base_price) / base_price) * 100

        triggered = False
        if alert.condition == 'increase' and pct_change >= float(alert.percentage_threshold):
            triggered = True
        elif alert.condition == 'decrease' and pct_change <= -float(alert.percentage_threshold):
            triggered = True

        if not triggered:
            continue

        logger.info(
            f"🔔 Alert triggered: {alert} | change={pct_change:.3f}% | "
            f"user={alert.user.username}"
        )

        pref = getattr(alert.user, 'profile', None)
        notif_pref = pref.notification_preference if pref else 'email'

        from rates.models import GoldSilverRate
        prev_rate = GoldSilverRate.objects.filter(
            metal=alert.metal
        ).exclude(id=rate_obj.id).first()
        previous_price = float(prev_rate.price_usd) if prev_rate else base_price

        sent_channels = ['browser']
        failed_channels = []

        if notif_pref in ('email', 'email_telegram'):
            ok = send_alert_email(
                alert.user, alert, current_price, previous_price, pct_change
            )
            (sent_channels if ok else failed_channels).append('email')

        if notif_pref in ('telegram', 'email_telegram'):
            ok = send_alert_telegram(
                alert.user, alert, current_price, previous_price, pct_change
            )
            (sent_channels if ok else failed_channels).append('telegram')

        for channel in sent_channels + failed_channels:
            NotificationHistory.objects.create(
                user=alert.user,
                alert=alert,
                metal=alert.metal,
                condition=alert.condition,
                percentage_triggered=round(pct_change, 4),
                price_at_trigger=current_price,
                previous_price=previous_price,
                channel=channel,
                message=(
                    f"{alert.get_metal_display()} {alert.condition} "
                    f"{abs(pct_change):.2f}% | ${current_price:.2f}/oz"
                ),
                status='sent' if channel in sent_channels else 'failed',
                is_read=False,
            )

        alert.last_triggered_at = timezone.now()
        alert.trigger_count += 1
        # Update base_price so the next alert is relative to this new price level
        alert.base_price = current_price
        alert.save(update_fields=['last_triggered_at', 'trigger_count', 'base_price'])


def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    interval = getattr(settings, 'PRICE_CHECK_INTERVAL_SECONDS', 60)
    _scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    _scheduler.add_job(
        check_alerts,
        trigger=IntervalTrigger(seconds=interval),
        id='price_check',
        replace_existing=True,
        misfire_grace_time=30,
    )
    _scheduler.start()
    logger.info(f"✅ Scheduler started — interval={interval}s")

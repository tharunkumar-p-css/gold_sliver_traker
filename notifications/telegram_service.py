import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_alert_telegram(user, alert, current_price, previous_price, pct_change):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(user.profile, 'telegram_chat_id', '')

    if not token or not chat_id:
        logger.warning(f"No Telegram config or chat ID for {user.username}")
        return False

    direction = "🚀 *Increased*" if pct_change > 0 else "📉 *Decreased*"
    metal_name = alert.get_metal_display().upper()
    
    message = (
        f"🔔 *GoldTracker: {metal_name} Alert*\n\n"
        f"The price of {metal_name} has {direction} beyond your *{alert.percentage_threshold}%* threshold.\n\n"
        f"💹 *Current Price:* ${current_price:,.2f}/oz\n"
        f"📍 *Starting Price:* ${previous_price:,.2f}/oz\n"
        f"📈 *Total Change:* {pct_change:+.2f}%\n\n"
        f"✅ *Note:* Your alert base price has been reset to ${current_price:,.2f} for the next move.\n\n"
        f"🔗 [Open Dashboard](http://localhost:8000/dashboard/)"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={
            'chat_id': chat_id, 
            'text': message, 
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        })
        logger.info(f"✅ Enhanced Telegram alert sent to {user.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Telegram alert failed for {user.username}: {e}")
        return False

def send_welcome_telegram(user):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(user.profile, 'telegram_chat_id', '')

    if not token or not chat_id:
        return False

    message = (
        f"👋 *Welcome to GoldTracker, {user.first_name}!*\n\n"
        f"Your account is now linked for *Instant Price Alerts*.\n\n"
        f"✅ *Monitoring:* Gold & Silver\n"
        f"⚡ *Speed:* Real-time (every 60s)\n"
        f"📈 *Charts:* Available on your Dashboard\n\n"
        f"You will receive a notification here as soon as your price targets are met!"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={
            'chat_id': chat_id, 
            'text': message, 
            'parse_mode': 'Markdown'
        })
        logger.info(f"✅ Enhanced Telegram welcome sent to {user.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Telegram welcome failed for {user.username}: {e}")
        return False

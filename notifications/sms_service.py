"""
notifications/sms_service.py
=============================
Sends SMS notifications via Twilio.
Falls back gracefully if Twilio credentials are not configured.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_alert_sms(user, alert, current_price, previous_price, pct_change):
    """
    Send an SMS price alert.
    """
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_PHONE_NUMBER

    if not all([sid, token, from_number]):
        return False

    phone = getattr(user.profile, 'phone_number', '')
    if not phone:
        return False

    direction = "increased" if pct_change > 0 else "decreased"
    body = (
        f"🚨 GoldTracker Alert\n"
        f"{alert.get_metal_display()} price {direction} by {abs(pct_change):.2f}%\n"
        f"Current: ₹{current_price:.2f}/g\n"
        f"Previous: ₹{previous_price:.2f}/g\n"
        f"Target: {alert.percentage_threshold}%"
    )

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(body=body, from_=from_number, to=phone)
        return True
    except Exception as e:
        logger.error(f"SMS Error: {e}")
        return False


def send_alert_whatsapp(user, alert, current_price, previous_price, pct_change):
    """
    Send a WhatsApp price alert via Twilio.
    """
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_number = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"

    if not all([sid, token, settings.TWILIO_PHONE_NUMBER]):
        return False

    phone = getattr(user.profile, 'phone_number', '')
    if not phone:
        return False
    
    to_number = f"whatsapp:{phone}"

    direction = "increased" if pct_change > 0 else "decreased"
    body = (
        f"🚨 *GoldTracker Alert*\n\n"
        f"The price of *{alert.get_metal_display()}* has {direction} by *{abs(pct_change):.2f}%*.\n\n"
        f"💰 *Current Price:* ₹{current_price:.2f}/g\n"
        f"📉 *Previous Price:* ₹{previous_price:.2f}/g\n"
        f"🎯 *Target Threshold:* {alert.percentage_threshold}%\n\n"
        f"Check your dashboard for live charts!"
    )

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(body=body, from_=from_number, to=to_number)
        return True
    except Exception as e:
        logger.error(f"WhatsApp Error: {e}")
        return False


def send_welcome_sms(user):
    """
    Send a welcome SMS upon successful registration if phone number is provided.
    """
    sid = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_PHONE_NUMBER

    if not all([sid, token, from_number]):
        logger.warning("Twilio credentials not configured — Welcome SMS skipped.")
        return False

    phone = getattr(user.profile, 'phone_number', '')
    if not phone:
        logger.info(f"No phone number for user {user.username} — Welcome SMS skipped.")
        return False

    body = (
        f"🎉 Welcome to GoldTracker, {user.first_name or user.username}!\n"
        "Your account is ready. You can now set up real-time gold and silver price alerts."
    )

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        message = client.messages.create(body=body, from_=from_number, to=phone)
        logger.info(f"✅ Welcome SMS sent to {phone} | SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"❌ Welcome SMS failed for {phone}: {e}")
        return False

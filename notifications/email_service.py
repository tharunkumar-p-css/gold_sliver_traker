import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def send_alert_email(user, alert, current_price, previous_price, pct_change):
    try:
        subject = f"GoldTracker Alert: {alert.get_metal_display()} {alert.get_condition_display()} {alert.percentage_threshold}%"
        html_content = render_to_string('emails/alert_email.html', {
            'user': user,
            'alert': alert,
            'current_price': current_price,
            'previous_price': previous_price,
            'pct_change': pct_change,
            'target_price': alert.target_price if hasattr(alert, 'target_price') else 0,
        })
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"✅ Alert email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"❌ Alert email failed for {user.email}: {e}")
        return False

def send_welcome_email(user):
    try:
        subject = "Welcome to GoldTracker!"
        html_content = render_to_string('emails/welcome_email.html', {
            'user': user,
        })
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"✅ Welcome email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"❌ Welcome email failed for {user.email}: {e}")
        return False

def send_login_email(user):
    try:
        subject = "Welcome Back to GoldTracker!"
        html_content = render_to_string('emails/login_email.html', {
            'user': user,
            'time': timezone.now() if 'timezone' in globals() else None,
        })
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"✅ Login notification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"❌ Login notification email failed for {user.email}: {e}")
        return False

"""
core/models.py
==============
UserProfile  — extends Django's built-in User with phone, country,
               currency preference, and notification channel.
UserAlert    — stores a user's custom percentage-based price alert.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'INR Indian Rupee'),
        ('USD', '$ US Dollar'),
        ('EUR', '€ Euro'),
        ('GBP', '£ British Pound'),
    ]
    NOTIFICATION_CHOICES = [
        ('email', 'Email Only'),
        ('telegram', 'Telegram Only'),
        ('email_telegram', 'Email + Telegram'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='India')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    notification_preference = models.CharField(
        max_length=20, choices=NOTIFICATION_CHOICES, default='email'
    )
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile whenever a new User is saved."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class UserAlert(models.Model):
    METAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
    ]
    CONDITION_CHOICES = [
        ('increase', 'Price Increases By'),
        ('decrease', 'Price Decreases By'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    metal = models.CharField(max_length=10, choices=METAL_CHOICES)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    # Threshold percentage (e.g. 5.0 means "notify when ±5% is hit")
    percentage_threshold = models.DecimalField(max_digits=5, decimal_places=2)
    # Price at the time this alert was created — used as the base for % calc
    base_price = models.DecimalField(max_digits=12, decimal_places=4)
    is_active = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        direction = '📈' if self.condition == 'increase' else '📉'
        return (
            f"{direction} {self.get_metal_display()} "
            f"{self.condition} {self.percentage_threshold}% "
            f"— {'Active' if self.is_active else 'Paused'}"
        )

    def target_price(self):
        """Calculate the exact price that would trigger this alert."""
        base = float(self.base_price)
        pct = float(self.percentage_threshold) / 100
        if self.condition == 'increase':
            return round(base * (1 + pct), 4)
        return round(base * (1 - pct), 4)

    class Meta:
        verbose_name = 'User Alert'
        verbose_name_plural = 'User Alerts'
        ordering = ['-created_at']

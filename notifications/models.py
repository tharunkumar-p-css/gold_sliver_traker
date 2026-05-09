"""
notifications/models.py
=======================
NotificationHistory — log of every alert notification dispatched.
"""
from django.db import models
from django.contrib.auth.models import User


class NotificationHistory(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('browser', 'Browser'),
        ('telegram', 'Telegram'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    # The alert that triggered this notification (nullable if alert deleted)
    alert = models.ForeignKey(
        'core.UserAlert', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notification_logs'
    )
    metal = models.CharField(max_length=10)
    condition = models.CharField(max_length=10)  # increase / decrease
    percentage_triggered = models.DecimalField(max_digits=8, decimal_places=4)
    price_at_trigger = models.DecimalField(max_digits=12, decimal_places=4)
    previous_price = models.DecimalField(max_digits=12, decimal_places=4)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_detail = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} | {self.metal} {self.condition} "
            f"{self.percentage_triggered}% | {self.channel} | {self.status}"
        )

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']

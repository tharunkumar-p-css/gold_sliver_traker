"""
rates/models.py
===============
GoldSilverRate — snapshot of gold/silver price at a point in time.
"""
from django.db import models


class GoldSilverRate(models.Model):
    METAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
    ]

    metal = models.CharField(max_length=10, choices=METAL_CHOICES)
    # Price per gram in INR and USD
    price_inr = models.DecimalField(max_digits=12, decimal_places=4)
    price_usd = models.DecimalField(max_digits=12, decimal_places=4)
    # Daily high / low (per gram, INR)
    daily_high = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    daily_low = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    # Percentage change vs. previous snapshot
    percentage_change = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    # USD→INR conversion rate used
    usd_inr_rate = models.DecimalField(max_digits=8, decimal_places=4, default=83.5)
    # Raw troy-oz price from API (USD)
    raw_price_oz_usd = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_metal_display()} ${self.price_usd}/oz @ {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        verbose_name = 'Gold/Silver Rate'
        verbose_name_plural = 'Gold/Silver Rates'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metal', 'timestamp']),
        ]

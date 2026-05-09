from django.contrib import admin
from rates.models import GoldSilverRate


@admin.register(GoldSilverRate)
class GoldSilverRateAdmin(admin.ModelAdmin):
    list_display = ['metal', 'price_inr', 'price_usd', 'daily_high', 'daily_low',
                    'percentage_change', 'usd_inr_rate', 'timestamp']
    list_filter = ['metal']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

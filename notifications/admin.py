from django.contrib import admin
from notifications.models import NotificationHistory


@admin.register(NotificationHistory)
class NotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'metal', 'condition', 'percentage_triggered',
                    'price_at_trigger', 'channel', 'status', 'sent_at']
    list_filter = ['metal', 'channel', 'status']
    search_fields = ['user__username', 'message']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'

from django.contrib import admin
from core.models import UserProfile, UserAlert


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'country', 'currency', 'notification_preference']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['country', 'currency', 'notification_preference']


@admin.register(UserAlert)
class UserAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'metal', 'condition', 'percentage_threshold',
                    'base_price', 'is_active', 'trigger_count', 'last_triggered_at']
    list_filter = ['metal', 'condition', 'is_active']
    search_fields = ['user__username']
    list_editable = ['is_active']
    readonly_fields = ['trigger_count', 'last_triggered_at', 'created_at']

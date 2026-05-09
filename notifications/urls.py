from django.urls import path
from notifications import views

urlpatterns = [
    path('', views.notification_history, name='notification_history'),
    path('api/unread/', views.api_get_notifications, name='api_get_notifications'),
    path('api/mark-read/', views.api_mark_notifications_read, name='api_mark_notifications_read'),
]

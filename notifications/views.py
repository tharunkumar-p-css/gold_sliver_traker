"""
notifications/views.py — Notification history page.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from notifications.models import NotificationHistory


@login_required
def notification_history(request):
    logs = NotificationHistory.objects.filter(user=request.user).select_related('alert')
    # Filter by channel/status
    channel = request.GET.get('channel', '')
    status = request.GET.get('status', '')
    if channel:
        logs = logs.filter(channel=channel)
    if status:
        logs = logs.filter(status=status)

    paginator = Paginator(logs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'notifications/history.html', {
        'page_obj': page,
        'channel_filter': channel,
        'status_filter': status,
        'active_page': 'notifications',
    })


# ── In-App Notification APIs ──────────────────────────────────────────────────

@login_required
def api_get_notifications(request):
    """Return top 5 unread notifications for the bell dropdown."""
    notifications = NotificationHistory.objects.filter(
        user=request.user
    ).order_by('-sent_at')[:5]

    data = [
        {
            'id': n.id,
            'metal': n.metal,
            'message': n.message,
            'is_read': n.is_read,
            'time': n.sent_at.isoformat(),
        }
        for n in notifications
    ]
    
    unread_count = NotificationHistory.objects.filter(user=request.user, is_read=False).count()
    
    return JsonResponse({
        'notifications': data,
        'unread_count': unread_count
    })


@login_required
def api_mark_notifications_read(request):
    """Mark all unread notifications for the user as read."""
    NotificationHistory.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

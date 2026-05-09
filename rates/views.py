"""
rates/views.py — Dashboard and JSON API views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from rates.models import GoldSilverRate
from rates.services import get_latest_rate
from core.models import UserAlert
from notifications.models import NotificationHistory
from rates.ai_prediction import predict_future_price
from rates.reports import generate_rate_pdf
from django.http import HttpResponse


@login_required
def dashboard(request):
    gold = get_latest_rate('gold')
    silver = get_latest_rate('silver')
    active_alerts = UserAlert.objects.filter(user=request.user, is_active=True).count()
    total_alerts = UserAlert.objects.filter(user=request.user).count()
    recent_notifications = NotificationHistory.objects.filter(
        user=request.user
    ).select_related('alert')[:5]

    return render(request, 'dashboard/index.html', {
        'gold': gold,
        'silver': silver,
        'active_alerts': active_alerts,
        'total_alerts': total_alerts,
        'recent_notifications': recent_notifications,
        'active_page': 'dashboard',
    })


# ── REST-style JSON APIs (used by dashboard AJAX) ─────────────────────────────

@login_required
def api_current_rates(request):
    """Return latest gold + silver rates as JSON."""
    gold = get_latest_rate('gold')
    silver = get_latest_rate('silver')

    def rate_dict(r):
        if not r:
            return None
        return {
            'price_inr': float(r.price_inr),
            'price_usd': float(r.price_usd),
            'daily_high': float(r.daily_high),
            'daily_low': float(r.daily_low),
            'pct_change': float(r.percentage_change),
            'usd_inr': float(r.usd_inr_rate),
            'updated': r.timestamp.isoformat(),
        }

    return JsonResponse({'gold': rate_dict(gold), 'silver': rate_dict(silver)})


@login_required
def api_rate_history(request):
    """Return last 24h of price snapshots for Chart.js."""
    metal = request.GET.get('metal', 'gold')
    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)

    qs = GoldSilverRate.objects.filter(
        metal=metal, timestamp__gte=since
    ).order_by('timestamp').values('timestamp', 'price_usd', 'percentage_change')

    data = [
        {
            'time': r['timestamp'].isoformat(),
            'price': float(r['price_usd']),
            'pct': float(r['percentage_change']),
        }
        for r in qs
    ]
    return JsonResponse({'metal': metal, 'history': data})
@login_required
def api_prediction(request):
    """Return AI prediction for gold/silver."""
    metal = request.GET.get('metal', 'gold')
    price, summary = predict_future_price(metal)
    return JsonResponse({'metal': metal, 'predicted_price': price, 'summary': summary})


@login_required
def download_report(request, metal):
    """Generate and return PDF report."""
    pdf = generate_rate_pdf(metal)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{metal}_report.pdf"'
    return response

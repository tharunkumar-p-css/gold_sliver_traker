"""
core/views.py — Auth, Profile, and Alert CRUD views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from core.forms import RegisterForm, LoginForm, ProfileForm, AlertForm
from core.models import UserAlert
from rates.services import get_latest_rate
from notifications.email_service import send_welcome_email, send_login_email
from notifications.telegram_service import send_welcome_telegram, send_login_telegram

# ── Authentication ────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        
        # Dispatch Real Notifications
        send_welcome_email(user)
        send_welcome_telegram(user)
        
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}! Your account is ready. 🎉")
        return redirect('dashboard')
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        
        # Dispatch Login Notifications
        send_login_email(user)
        send_login_telegram(user)
        
        messages.success(request, f"Welcome back, {user.first_name or user.username}! 👋")
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out. See you soon!")
    return redirect('login')


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully! ✅")
        return redirect('profile')
    return render(request, 'auth/profile.html', {'form': form, 'active_page': 'profile'})


# ── Alerts CRUD ───────────────────────────────────────────────────────────────

@login_required
def alert_list(request):
    alerts = UserAlert.objects.filter(user=request.user)
    gold_rate = get_latest_rate('gold')
    silver_rate = get_latest_rate('silver')
    return render(request, 'alerts/list.html', {
        'alerts': alerts,
        'gold_rate': gold_rate,
        'silver_rate': silver_rate,
        'active_page': 'alerts',
    })


@login_required
def alert_create(request):
    gold_rate = get_latest_rate('gold')
    silver_rate = get_latest_rate('silver')
    form = AlertForm(request.POST or None)
    if form.is_valid():
        alert = form.save(commit=False)
        alert.user = request.user
        # Set base price from current market price
        metal = alert.metal
        rate = gold_rate if metal == 'gold' else silver_rate
        alert.base_price = rate.price_usd if rate else 2350
        alert.save()
        messages.success(request, f"Alert created! You'll be notified when {alert}. 🔔")
        return redirect('alert_list')
    return render(request, 'alerts/create.html', {
        'form': form,
        'gold_rate': gold_rate,
        'silver_rate': silver_rate,
        'active_page': 'alerts',
    })


@login_required
def alert_edit(request, pk):
    alert = get_object_or_404(UserAlert, pk=pk, user=request.user)
    form = AlertForm(request.POST or None, instance=alert)
    if form.is_valid():
        form.save()
        messages.success(request, "Alert updated! ✅")
        return redirect('alert_list')
    return render(request, 'alerts/edit.html', {'form': form, 'alert': alert, 'active_page': 'alerts'})


@login_required
def alert_delete(request, pk):
    alert = get_object_or_404(UserAlert, pk=pk, user=request.user)
    if request.method == 'POST':
        alert.delete()
        messages.success(request, "Alert deleted.")
        return redirect('alert_list')
    return render(request, 'alerts/confirm_delete.html', {'alert': alert, 'active_page': 'alerts'})


@login_required
@require_POST
def alert_toggle(request, pk):
    """AJAX endpoint — toggle alert active/inactive."""
    alert = get_object_or_404(UserAlert, pk=pk, user=request.user)
    alert.is_active = not alert.is_active
    alert.save(update_fields=['is_active'])
    return JsonResponse({'is_active': alert.is_active})

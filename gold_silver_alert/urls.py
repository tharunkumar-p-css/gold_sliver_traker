"""gold_silver_alert URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls')),
    path('dashboard/', include('rates.urls')),
    path('alerts/', include('core.alert_urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('rates.api_urls')),
    # Built-in password reset
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from rates import views

urlpatterns = [
    path('rates/current/', views.api_current_rates, name='api_current_rates'),
    path('rates/history/', views.api_rate_history, name='api_rate_history'),
    path('rates/prediction/', views.api_prediction, name='api_prediction'),
]

from django.urls import path
from rates import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('report/<str:metal>/', views.download_report, name='download_report'),
]

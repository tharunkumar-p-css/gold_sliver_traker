from django.urls import path
from core import views

urlpatterns = [
    path('', views.alert_list, name='alert_list'),
    path('create/', views.alert_create, name='alert_create'),
    path('<int:pk>/edit/', views.alert_edit, name='alert_edit'),
    path('<int:pk>/delete/', views.alert_delete, name='alert_delete'),
    path('<int:pk>/toggle/', views.alert_toggle, name='alert_toggle'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/summary/', views.api_summary, name='api_summary'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/simulate/', views.api_simulate, name='api_simulate'),
]

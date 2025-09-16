from django.contrib import admin
from .models import Hospital, Recurso


admin.site.register(Hospital)
admin.site.register(Recurso)




### FILE: dashboard/urls.py
from django.urls import path
from . import views


app_name = 'dashboard'


urlpatterns = [
path('', views.home, name='home'),
path('mapa/', views.mapa, name='mapa'),
path('recursos/', views.recursos, name='recursos'),
path('api/kpis/', views.kpis_json, name='kpis_json'),
]   
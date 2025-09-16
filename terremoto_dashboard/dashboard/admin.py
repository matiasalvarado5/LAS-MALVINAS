from django.contrib import admin
from .models import IncidentSummary

@admin.register(IncidentSummary)
class IncidentSummaryAdmin(admin.ModelAdmin):
    list_display = ('created_at','population','fatalities','hospital_operational_pct')

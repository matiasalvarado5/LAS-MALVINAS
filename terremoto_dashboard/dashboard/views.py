from django.shortcuts import render
from django.http import JsonResponse
from .models import IncidentSummary, Bridge, Hospital, Shelter, ServiceStatus, MetricPoint
from django.views.decorators.http import require_POST
from django.utils import timezone

def dashboard_view(request):
    summary = IncidentSummary.objects.order_by('-created_at').first()
    if not summary:
        summary = IncidentSummary.objects.create()
    # Enviamos datos iniciales (el template pedirá datos via /api/)
    context = {"summary": summary}
    return render(request, 'dashboard/dashboard.html', context)

def api_summary(request):
    summary = IncidentSummary.objects.order_by('-created_at').first()
    if not summary:
        summary = IncidentSummary.objects.create()
    data = summary.to_dict()
    # añadir recursos persistidos
    data.update({
        "coords": {"lat": -35.020694, "lng": -69.323999},
        "bridges": [b.to_dict() for b in Bridge.objects.all()],
        "hospitals": [h.to_dict() for h in Hospital.objects.all()],
        "shelters": [s.to_dict() for s in Shelter.objects.all()],
        "services": [sv.to_dict() for sv in ServiceStatus.objects.all()],
    })
    return JsonResponse(data)

def api_metrics(request):
    """
    Devuelve series temporales agrupadas por metric.
    {
      "fatalities": [{timestamp, value}, ...],
      "hospital_capacity": [...]
    }
    """
    qs = MetricPoint.objects.order_by('timestamp')
    groups = {}
    for m in qs:
        groups.setdefault(m.metric, []).append({"timestamp": m.timestamp.isoformat(), "value": m.value})
    return JsonResponse(groups)

@require_POST
def api_simulate(request):
    # simular cambios y guardar metric points
    summary = IncidentSummary.objects.order_by('-created_at').first()
    if not summary:
        summary = IncidentSummary.objects.create()
    # cambios simples
    summary.fatalities = int(summary.fatalities * 1.05)
    summary.injured_severe_min = int(summary.injured_severe_min * 1.05)
    summary.injured_severe_max = int(summary.injured_severe_max * 1.10)
    summary.injured_mild_min = int(summary.injured_mild_min * 1.02)
    summary.injured_mild_max = int(summary.injured_mild_max * 1.05)
    summary.hospital_operational_pct = max(0.05, summary.hospital_operational_pct - 0.08)
    summary.save()

    # crear metric points (timestamp ahora)
    now = timezone.now()
    MetricPoint.objects.create(timestamp=now, metric='fatalities', value=summary.fatalities)
    MetricPoint.objects.create(timestamp=now, metric='injured_severe', value=summary.avg_injured_severe())
    MetricPoint.objects.create(timestamp=now, metric='injured_mild', value=summary.avg_injured_mild())
    MetricPoint.objects.create(timestamp=now, metric='hospital_operational_pct', value=summary.hospital_operational_pct * 100)

    return JsonResponse(summary.to_dict())

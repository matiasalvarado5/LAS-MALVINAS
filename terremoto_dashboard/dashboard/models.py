from django.db import models
from django.utils import timezone

class IncidentSummary(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    population = models.IntegerField(default=3500)
    affected_pct_min = models.FloatField(default=0.25)
    affected_pct_max = models.FloatField(default=0.35)
    shelter_needed_min = models.IntegerField(default=800)
    shelter_needed_max = models.IntegerField(default=900)
    hospital_operational_pct = models.FloatField(default=0.40)
    fatalities = models.IntegerField(default=80)
    injured_severe_min = models.IntegerField(default=60)
    injured_severe_max = models.IntegerField(default=80)
    injured_mild_min = models.IntegerField(default=800)
    injured_mild_max = models.IntegerField(default=900)

    def avg_affected(self):
        return int(((self.affected_pct_min + self.affected_pct_max) / 2) * self.population)

    def avg_injured_severe(self):
        return int((self.injured_severe_min + self.injured_severe_max) / 2)

    def avg_injured_mild(self):
        return int((self.injured_mild_min + self.injured_mild_max) / 2)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "population": self.population,
            "affected": self.avg_affected(),
            "shelter_min": self.shelter_needed_min,
            "shelter_max": self.shelter_needed_max,
            "hospital_operational_pct": self.hospital_operational_pct,
            "fatalities": self.fatalities,
            "injured_severe": self.avg_injured_severe(),
            "injured_mild": self.avg_injured_mild(),
        }

class Bridge(models.Model):
    name = models.CharField(max_length=120)
    lat = models.FloatField()
    lng = models.FloatField()
    status = models.CharField(max_length=50, choices=[('derribado','Derribado'),('parcialmente','Parcialmente dañado'),('ok','Operativo')], default='derribado')
    notes = models.TextField(blank=True, default='')

    def to_dict(self):
        return {"id": self.id, "name": self.name, "lat": self.lat, "lng": self.lng, "status": self.status, "notes": self.notes}

    def __str__(self):
        return f"{self.name} ({self.status})"

class Hospital(models.Model):
    name = models.CharField(max_length=120)
    lat = models.FloatField()
    lng = models.FloatField()
    total_beds = models.IntegerField(default=50)
    available_beds = models.IntegerField(default=20)
    operational = models.BooleanField(default=True)

    def occupancy_pct(self):
        if self.total_beds == 0: return 0
        used = self.total_beds - self.available_beds
        return round((used / self.total_beds) * 100, 1)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "lat": self.lat, "lng": self.lng, "total_beds": self.total_beds, "available_beds": self.available_beds, "operational": self.operational, "occupancy_pct": self.occupancy_pct()}

    def __str__(self):
        return f"{self.name} - {self.total_beds} camas"

class Shelter(models.Model):
    name = models.CharField(max_length=120)
    lat = models.FloatField()
    lng = models.FloatField()
    capacity = models.IntegerField(default=100)
    occupants = models.IntegerField(default=0)

    def occupancy_pct(self):
        if self.capacity == 0: return 0
        return round((self.occupants / self.capacity) * 100, 1)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "lat": self.lat, "lng": self.lng, "capacity": self.capacity, "occupants": self.occupants, "occupancy_pct": self.occupancy_pct()}

    def __str__(self):
        return f"{self.name} ({self.occupants}/{self.capacity})"

class ServiceStatus(models.Model):
    name = models.CharField(max_length=80)  # e.g., Electricity, Water, Communications
    status = models.CharField(max_length=80) # e.g., 'Corte total', 'Parcial', 'Operativo'
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "status": self.status, "note": self.note, "updated_at": self.updated_at.isoformat()}

class MetricPoint(models.Model):
    """
    Serie temporal simple para métricas en horas desde el evento:
    tipo: 'fatalities','injured_mild','hospital_capacity', etc.
    """
    timestamp = models.DateTimeField(default=timezone.now)
    metric = models.CharField(max_length=80)
    value = models.FloatField()
    note = models.TextField(blank=True)

    def to_dict(self):
        return {"id": self.id, "timestamp": self.timestamp.isoformat(), "metric": self.metric, "value": self.value, "note": self.note}

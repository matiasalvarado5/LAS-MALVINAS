# dashboard/management/commands/create_incident_from_enunciado.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import IncidentSummary, Bridge, Hospital, Shelter, ServiceStatus, MetricPoint
import datetime

class Command(BaseCommand):
    help = "Crea/actualiza datos reales del enunciado del terremoto de Las Malvinas (San Rafael)"

    def handle(self, *args, **options):
        # --- 1) Crear o actualizar IncidentSummary según enunciado ---
        # Datos tomados textualmente del enunciado del usuario
        population = 3500
        affected_pct_min = 0.25
        affected_pct_max = 0.35
        shelter_needed_min = 800
        shelter_needed_max = 900
        hospital_operational_pct = 0.40  # 40% operativa inicial departamental
        fatalities_est = 80  # fallecidos proyectados (en 72h)
        injured_severe_min = 60
        injured_severe_max = 80
        injured_mild_min = 800
        injured_mild_max = 900

        # Crear o actualizar único resumen más reciente
        summary = IncidentSummary.objects.order_by('-created_at').first()
        if not summary:
            summary = IncidentSummary.objects.create(
                population=population,
                affected_pct_min=affected_pct_min,
                affected_pct_max=affected_pct_max,
                shelter_needed_min=shelter_needed_min,
                shelter_needed_max=shelter_needed_max,
                hospital_operational_pct=hospital_operational_pct,
                fatalities=fatalities_est,
                injured_severe_min=injured_severe_min,
                injured_severe_max=injured_severe_max,
                injured_mild_min=injured_mild_min,
                injured_mild_max=injured_mild_max
            )
            self.stdout.write(self.style.SUCCESS("IncidentSummary creado."))
        else:
            # actualizar campos relevantes
            summary.population = population
            summary.affected_pct_min = affected_pct_min
            summary.affected_pct_max = affected_pct_max
            summary.shelter_needed_min = shelter_needed_min
            summary.shelter_needed_max = shelter_needed_max
            summary.hospital_operational_pct = hospital_operational_pct
            summary.fatalities = fatalities_est
            summary.injured_severe_min = injured_severe_min
            summary.injured_severe_max = injured_severe_max
            summary.injured_mild_min = injured_mild_min
            summary.injured_mild_max = injured_mild_max
            summary.save()
            self.stdout.write(self.style.SUCCESS("IncidentSummary actualizado."))

        # --- 2) Recursos: puentes, hospitales y refugios según enunciado ---
        # Puentes principales derribados (RP179 y RP175). Uso epicentro cercano y posiciones relativas aproximadas.
        # Si tenés coords exactas de cada puente, reemplazalas aquí.
        Bridge.objects.update_or_create(
            name='Puente RP179',
            defaults={'lat': -35.0215, 'lng': -69.3250, 'status': 'derribado', 'notes': 'Puente principal derribado según enunciado'}
        )
        Bridge.objects.update_or_create(
            name='Puente RP175',
            defaults={'lat': -35.0180, 'lng': -69.3200, 'status': 'derribado', 'notes': 'Segundo puente derribado — acceso estratégico interrumpido'}
        )
        self.stdout.write(self.style.SUCCESS("Puentes registrados/actualizados."))

        # Hospitals: en el enunciado se menciona saturación departamental y 40% operativa.
        # Creo dos hospitales representativos: el regional departamental (fuera del pueblo) y uno local afectado.
        Hospital.objects.update_or_create(
            name='Hospital Regional San Rafael',
            defaults={'lat': -34.616, 'lng': -68.333, 'total_beds': 200, 'available_beds': int(200 * (0.40)), 'operational': True}
        )
        Hospital.objects.update_or_create(
            name='Hospital Local Las Malvinas',
            defaults={'lat': -35.022, 'lng': -69.3235, 'total_beds': 30, 'available_beds': int(30 * 0.10), 'operational': False}
        )
        self.stdout.write(self.style.SUCCESS("Hospitales creados/actualizados."))

        # Shelters: el enunciado menciona 800-900 que necesitan albergue. Crear refugios con capacidad.
        Shelter.objects.update_or_create(
            name='Polideportivo Las Malvinas',
            defaults={'lat': -35.0195, 'lng': -69.3245, 'capacity': 350, 'occupants': 350}
        )
        Shelter.objects.update_or_create(
            name='Escuela Principal Las Malvinas',
            defaults={'lat': -35.0230, 'lng': -69.3210, 'capacity': 300, 'occupants': 300}
        )
        Shelter.objects.update_or_create(
            name='Refugio Provisorio - Plaza Central',
            defaults={'lat': -35.0200, 'lng': -69.3230, 'capacity': 300, 'occupants': 150}
        )
        self.stdout.write(self.style.SUCCESS("Refugios creados/actualizados."))

        # --- 3) Servicios básicos según enunciado ---
        # Energía, agua, comunicaciones, radio local
        ServiceStatus.objects.update_or_create(
            name='Electricidad',
            defaults={'status': 'Corte total', 'note': '100% sin suministro; postes y transformadores dañados'}
        )
        ServiceStatus.objects.update_or_create(
            name='Agua',
            defaults={'status': 'Cortes y baja presión (20-35%)', 'note': 'Rotura de matrices principales, riesgo de contaminación'}
        )
        ServiceStatus.objects.update_or_create(
            name='Comunicaciones móviles',
            defaults={'status': 'Sin telefonía móvil ni internet', 'note': 'Operadores no disponibles; VHF/UHF como respaldo'}
        )
        ServiceStatus.objects.update_or_create(
            name='Radio local',
            defaults={'status': 'Activa', 'note': 'Canal principal de información a la comunidad'}
        )
        self.stdout.write(self.style.SUCCESS("Estados de servicios creados/actualizados."))

        # --- 4) MetricPoints: serie temporal representativa (0h, 12h, 24h, 48h, 72h) ---
        # Vaciamos metric points antiguos para no duplicar
        MetricPoint.objects.filter(metric__in=['fatalities','injured_severe','injured_mild','hospital_operational_pct']).delete()

        base_fatalities = fatalities_est  # 80 proyectados en 72h; distribuyo hacia atrás suponiendo crecimiento
        # Supongamos una progresión: 0h -> 60% del total proyectado; 12h -> 70%; 24h -> 85%; 48h -> 95%; 72h -> 100%
        timeline = [
            (0, 0.60),
            (12, 0.70),
            (24, 0.85),
            (48, 0.95),
            (72, 1.00)
        ]
        now = timezone.now()
        for hours, frac in timeline:
            ts = now - datetime.timedelta(hours=(72 - hours))  # timeline hacia atrás desde ahora (72h total)
            fatalities_val = int(round(base_fatalities * frac))
            MetricPoint.objects.create(timestamp=ts, metric='fatalities', value=fatalities_val, note=f'{hours}h desde evento (estimación)')
            # Heridos graves: usar rango medio y similar progresión
            base_severe = int((injured_severe_min + injured_severe_max) / 2)
            severe_val = int(round(base_severe * (1 + 0.1 * (hours/24))))  # crecimiento suave
            MetricPoint.objects.create(timestamp=ts, metric='injured_severe', value=severe_val, note=f'{hours}h desde evento')
            # Heridos leves
            base_mild = int((injured_mild_min + injured_mild_max) / 2)
            mild_val = int(round(base_mild * (1 + 0.06 * (hours/24))))
            MetricPoint.objects.create(timestamp=ts, metric='injured_mild', value=mild_val, note=f'{hours}h desde evento')
            # Hospital operational pct (convertido a %)
            # Asumimos baja progresiva: 0h -> 40%, 12h -> 36%, 24h -> 30%, 48h -> 20%, 72h -> 15%
            if hours == 0:
                hosp_pct = 40
            elif hours == 12:
                hosp_pct = 36
            elif hours == 24:
                hosp_pct = 30
            elif hours == 48:
                hosp_pct = 20
            else:
                hosp_pct = 15
            MetricPoint.objects.create(timestamp=ts, metric='hospital_operational_pct', value=hosp_pct, note=f'{hours}h desde evento')

        self.stdout.write(self.style.SUCCESS("MetricPoints creados para 0h,12h,24h,48h,72h."))

        # --- 5) Información adicional (clima y notas) ---
        # Podemos guardar clima como ServiceStatus o agregar un registro de note en IncidentSummary, 
        # pero para simplicidad creamos un ServiceStatus 'Clima' con la nota de -3°C nocturno.
        ServiceStatus.objects.update_or_create(
            name='Clima (noches)',
            defaults={'status': 'Frío -3°C nocturno', 'note': 'Riesgo de hipotermia; demanda de calefacción y energía crítica'}
        )
        self.stdout.write(self.style.SUCCESS("Estado de clima agregado."))

        # Mensaje final
        self.stdout.write(self.style.SUCCESS("Datos del enunciado cargados correctamente. Revisa /api/summary/ y /api/metrics/ en tu app."))

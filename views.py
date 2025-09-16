from django.shortcuts import render
from django.http import JsonResponse
from .models import Hospital, Recurso
import pandas as pd
import plotly.express as px
import plotly.offline as po
import json
from django.templatetags.static import static


# Datos base (del enunciado)
POBLACION = 3500
FALLECIDOS = 80
HERIDOS_GRAVES = 70
HERIDOS_LEVES = 850
AFECTADOS = int(POBLACION * 0.30)
CAP_HOSP = 40
MAGNITUD = 7.0




def home(request):
# Preparar gráfico de víctimas con Plotly y pasarlo como div
df = pd.DataFrame({
'Categoría': ['Fallecidos', 'Heridos graves', 'Heridos leves', 'Afectados (albergue)'],
'Cantidad': [FALLECIDOS, HERIDOS_GRAVES, HERIDOS_LEVES, AFECTADOS]
})
fig = px.bar(df, x='Categoría', y='Cantidad', text='Cantidad', title='Víctimas y personas a asistir')
graph_div = po.plot(fig, include_plotlyjs=False, output_type='div')


context = {
'poblacion': POBLACION,
'afectados': AFECTADOS,
'fallecidos': FALLECIDOS,
'cap_hosp': CAP_HOSP,
'magnitud': MAGNITUD,
'plot_div': graph_div,
}
return render(request, 'dashboard/home.html', context)




def mapa(request):
# cargar hospitales desde DB (si existen)
hospitales = list(Hospital.objects.all().values())
context = {'hospitales': hospitales}
return render(request, 'dashboard/mapa.html', context)




def recursos(request):
recursos = list(Recurso.objects.all())
return render(request, 'dashboard/recursos.html', {'recursos': recursos})




def kpis_json(request):
data = {
'poblacion': POBLACION,
'afectados': AFECTADOS,
'fallecidos': FALLECIDOS,
'cap_hosp': CAP_HOSP,
'magnitud': MAGNITUD,
}
return JsonResponse(data)
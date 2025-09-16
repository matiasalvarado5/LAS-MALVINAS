from django.db import models


class Hospital(models.Model):
nombre = models.CharField(max_length=200)
lat = models.FloatField()
lon = models.FloatField()
capacidad_total = models.IntegerField()
capacidad_operativa = models.IntegerField()


def __str__(self):
return self.nombre


class Recurso(models.Model):
nombre = models.CharField(max_length=200)
cantidad = models.IntegerField()
ubicacion = models.CharField(max_length=200, blank=True)


def __str__(self):
return self.nombre
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.dispatch import receiver

# Create your models here.


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    numero = models.BigIntegerField()
    patente = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nombre





class Planillas(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # Puede ser 'correctiva' o 'preventiva'
    lista_tipo = models.CharField(max_length=20)

    def __str__(self):
        return f'Planilla {self.id} - Cliente: {self.cliente.nombre}'


class PlanillaCliente(models.Model):
    planillaId = models.ForeignKey(Planillas, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    cambio = models.BooleanField(default=False)
    checkbox = models.BooleanField(default=False)
    observaciones = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(default=datetime.today)
    planilla = models.ForeignKey(
        Planillas, on_delete=models.CASCADE, null=True, blank=True)
    kilometros = models.IntegerField()
    proxservicio = models.DateField()
    mecanico = models.ForeignKey(User, on_delete=models.CASCADE)


class ListaCorrectiva(models.Model):
    items = models.CharField(max_length=255)


class ListaPreventiva(models.Model):
    items = models.CharField(max_length=255)

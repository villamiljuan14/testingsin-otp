from django.db import models


class Vehiculo(models.Model):
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    año = models.PositiveIntegerField()
    capacidad = models.PositiveIntegerField(help_text='Capacidad en kg')
    estado = models.CharField(max_length=20, default='DISPONIBLE')

    class Meta:
        db_table = 'vehiculos_vehiculo'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'


class Conductor(models.Model):
    usuario = models.OneToOneField(
        'Autenticacion.Usuario',
        on_delete=models.CASCADE,
        related_name='conductor_profile'
    )
    licencia = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, default='ACTIVO')

    class Meta:
        db_table = 'vehiculos_conductor'
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'

    def __str__(self):
        return f'{self.usuario.get_full_name()} - {self.licencia}'

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# ── CHOICES ──

class EstadoRuta(models.TextChoices):
    BORRADOR = 'BORRADOR', 'Borrador'
    PLANIFICADA = 'PLANIFICADA', 'Planificada'
    ASIGNADA = 'ASIGNADA', 'Asignada'
    EN_ESPERA = 'EN_ESPERA', 'En Espera de Inicio'
    EN_CURSO = 'EN_CURSO', 'En Curso'
    PAUSADA = 'PAUSADA', 'Pausada'
    DESVIADA = 'DESVIADA', 'Desviada de Ruta'
    COMPLETADA = 'COMPLETADA', 'Completada'
    PARCIALMENTE_COMPLETADA = 'PARCIALMENTE_COMPLETADA', 'Parcialmente Completada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    POSTERGADA = 'POSTERGADA', 'Postergada'

class PrioridadRuta(models.TextChoices):
    BAJA = 'BAJA', 'Baja'
    NORMAL = 'NORMAL', 'Normal'
    ALTA = 'ALTA', 'Alta'
    URGENTE = 'URGENTE', 'Urgente'
    CRITICA = 'CRITICA', 'Crítica'

class EstadoVehiculo(models.TextChoices):
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    EN_RUTA = 'EN_RUTA', 'En Ruta'
    MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
    INACTIVO = 'INACTIVO', 'Inactivo'

class TipoOptimizacion(models.TextChoices):
    DISTANCIA = 'DISTANCIA', 'Minimizar Distancia'
    TIEMPO = 'TIEMPO', 'Minimizar Tiempo'
    COSTO = 'COSTO', 'Minimizar Costo'
    COMBINADO = 'COMBINADO', 'Optimización Combinada'
    MANUAL = 'MANUAL', 'Manual (sin optimizar)'

class TipoZona(models.TextChoices):
    URBANA = 'URBANA', 'Zona Urbana'
    SUBURBANA = 'SUBURBANA', 'Zona Suburbana'
    RURAL = 'RURAL', 'Zona Rural'
    INDUSTRIAL = 'INDUSTRIAL', 'Zona Industrial'
    COMERCIAL = 'COMERCIAL', 'Zona Comercial'
    RESTRINGIDA = 'RESTRINGIDA', 'Zona Restringida'

class MotivoAsignacion(models.TextChoices):
    ASIGNACION_NORMAL = 'ASIGNACION_NORMAL', 'Asignación Normal'
    REEMPLAZO = 'REEMPLAZO', 'Reemplazo'
    MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento del Vehículo'
    EMERGENCIA = 'EMERGENCIA', 'Emergencia'

# ── MODELOS ──

class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True, db_index=True)
    marca = models.CharField(max_length=50, null=True, blank=True)
    modelo = models.CharField(max_length=50, null=True, blank=True)
    anio = models.PositiveIntegerField(null=True, blank=True)
    tipo_vehiculo = models.CharField(max_length=45, null=True, blank=True)
    capacidad_peso_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacidad_volumen_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoVehiculo.choices, default=EstadoVehiculo.DISPONIBLE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rutas_vehiculo'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        app_label = 'Rutas'

    def __str__(self):
        return f'{self.placa} - {self.marca} {self.modelo}'

class Ruta(models.Model):
    codigo_ruta = models.CharField(max_length=50, unique=True, db_index=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    
    hub_origen = models.ForeignKey('Pedidos.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas_salida')
    hub_destino = models.ForeignKey('Pedidos.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas_llegada')
    
    estado = models.CharField(max_length=30, choices=EstadoRuta.choices, default=EstadoRuta.BORRADOR, blank=True)
    prioridad = models.CharField(max_length=20, choices=PrioridadRuta.choices, default=PrioridadRuta.NORMAL, blank=True)
    
    # ✅ Relaciones Directas (para simplificar Dashboard)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas')
    conductor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rutas_asignadas')
    
    fecha_programada = models.DateField(default=timezone.now)
    hora_salida_estimada = models.TimeField(null=True, blank=True)
    hora_retorno_estimada = models.TimeField(null=True, blank=True)
    hora_salida_real = models.TimeField(null=True, blank=True)
    hora_retorno_real = models.TimeField(null=True, blank=True)
    
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rutas_ruta'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'
        app_label = 'Rutas'

    def __str__(self):
        return f'{self.codigo_ruta} - {self.nombre}'

class ParadaRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='paradas')
    pedido = models.OneToOneField('Pedidos.Pedido', on_delete=models.PROTECT, related_name='parada_ruta', null=True, blank=True)
    orden_parada = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    direccion_completa = models.TextField()
    estado = models.CharField(max_length=30, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutas_parada_ruta'
        verbose_name = 'Parada de Ruta'
        verbose_name_plural = 'Paradas de Ruta'
        app_label = 'Rutas'

class AsignacionVehiculo(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='asignaciones_vehiculo')
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.PROTECT, related_name='asignaciones_ruta')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutas_asignacion_vehiculo'
        app_label = 'Rutas'

class AsignacionConductor(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='asignaciones_conductor')
    conductor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='asignaciones_ruta')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutas_asignacion_conductor'
        app_label = 'Rutas'

class ZonaCobertura(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    hub = models.ForeignKey('Pedidos.Hub', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TipoZona.choices, default=TipoZona.URBANA)
    centro_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    centro_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    radio_km = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'))

    class Meta:
        db_table = 'rutas_zona_cobertura'
        app_label = 'Rutas'

class ParametrosOptimizacion(models.Model):
    ruta = models.OneToOneField(Ruta, on_delete=models.CASCADE, related_name='parametros_optimizacion')
    tipo = models.CharField(max_length=20, choices=TipoOptimizacion.choices, default=TipoOptimizacion.DISTANCIA)

    class Meta:
        db_table = 'rutas_parametros_optimizacion'
        app_label = 'Rutas'

class MetricaRuta(models.Model):
    ruta = models.OneToOneField(Ruta, on_delete=models.CASCADE, related_name='metricas')
    distancia_planificada_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distancia_real_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_calculo = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutas_metrica_ruta'
        app_label = 'Rutas'

class HistorialCambiosRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='historial_cambios')
    campo_cambiado = models.CharField(max_length=100)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutas_historial_cambios'
        app_label = 'Rutas'

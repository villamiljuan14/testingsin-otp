from django.db import models
from decimal import Decimal
from django.db.models import Avg, Count, Q


class MetricaNovedad(models.Model):
    """
    Métricas y KPIs de gestión de novedades.
    Se calcula periódicamente para reporting.
    """
    # ✅ Período de la métrica
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # ✅ Totales
    total_novedades = models.PositiveIntegerField(default=0)
    novedades_resueltas = models.PositiveIntegerField(default=0)
    novedades_pendientes = models.PositiveIntegerField(default=0)
    novedades_canceladas = models.PositiveIntegerField(default=0)
    
    # ✅ Por severidad
    severidad_bajo = models.PositiveIntegerField(default=0)
    severidad_medio = models.PositiveIntegerField(default=0)
    severidad_alto = models.PositiveIntegerField(default=0)
    severidad_critico = models.PositiveIntegerField(default=0)
    severidad_emergencia = models.PositiveIntegerField(default=0)
    
    # ✅ SLA
    sla_cumplido = models.PositiveIntegerField(default=0)
    sla_vencido = models.PositiveIntegerField(default=0)
    porcentaje_cumplimiento_sla = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # ✅ Tiempos
    tiempo_promedio_respuesta_horas = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tiempo_promedio_resolucion_horas = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # ✅ Impacto
    impacto_economico_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    clientes_afectados_total = models.PositiveIntegerField(default=0)
    
    # ✅ Acciones correctivas
    total_acciones = models.PositiveIntegerField(default=0)
    acciones_efectivas = models.PositiveIntegerField(default=0)
    porcentaje_efectividad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # ✅ Escalamientos
    total_escaladas = models.PositiveIntegerField(default=0)
    porcentaje_escaladas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # ✅ Fecha de cálculo
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    calculado_por = models.CharField(max_length=100, default='SISTEMA')
    
    class Meta:
        db_table = 'novedades_metrica'
        verbose_name = 'Métrica de Novedades'
        verbose_name_plural = 'Métricas de Novedades'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
            models.Index(fields=['porcentaje_cumplimiento_sla']),
        ]
    
    def __str__(self):
        return f'Métricas {self.fecha_inicio} - {self.fecha_fin}'
    
    @classmethod
    def calcular_metricas(cls, fecha_inicio, fecha_fin):
        """Calcula métricas para un período determinado"""
        from django.utils import timezone
        from .novedad import Novedad
        from .accion_correctiva import AccionCorrectiva
        
        # ✅ Filtrar novedades del período
        novedades = Novedad.objects.filter(
            fecha_registro__range=[fecha_inicio, fecha_fin]
        )
        
        # ✅ Calcular totales
        total = novedades.count()
        resueltas = novedades.filter(estado='RESUELTA').count()
        pendientes = novedades.filter(estado__in=['REGISTRADA', 'EN_REVISION', 'ASIGNADA', 'EN_PROGRESO']).count()
        canceladas = novedades.filter(estado='CANCELADA').count()
        
        # ✅ Calcular por severidad
        severidades = {
            'BAJO': novedades.filter(severidad='BAJO').count(),
            'MEDIO': novedades.filter(severidad='MEDIO').count(),
            'ALTO': novedades.filter(severidad='ALTO').count(),
            'CRITICO': novedades.filter(severidad='CRITICO').count(),
            'EMERGENCIA': novedades.filter(severidad='EMERGENCIA').count(),
        }
        
        # ✅ Calcular SLA
        sla_cumplido = novedades.filter(sla_cumplido=True).count()
        sla_vencido = novedades.filter(sla_cumplido=False).count()
        porcentaje_sla = Decimal(str(round((sla_cumplido / total * 100) if total > 0 else 0, 2)))
        
        # ✅ Calcular tiempos promedio
        avg_respuesta = novedades.filter(
            tiempo_respuesta_horas__isnull=False
        ).aggregate(Avg('tiempo_respuesta_horas'))['tiempo_respuesta_horas__avg'] or Decimal('0.00')
        
        avg_resolucion = novedades.filter(
            tiempo_resolucion_horas__isnull=False
        ).aggregate(Avg('tiempo_resolucion_horas'))['tiempo_resolucion_horas__avg'] or Decimal('0.00')
        
        # ✅ Calcular impacto
        impacto_total = novedades.aggregate(
            total=Sum('impacto_economico')
        )['total'] or Decimal('0.00')
        
        clientes_afectados = novedades.aggregate(
            total=Sum('clientes_afectados')
        )['total'] or 0
        
        # ✅ Acciones correctivas
        acciones = AccionCorrectiva.objects.filter(novedad__in=novedades)
        total_acciones = acciones.count()
        acciones_efectivas = acciones.filter(efectiva=True).count()
        porcentaje_efectividad = Decimal(str(round((acciones_efectivas / total_acciones * 100) if total_acciones > 0 else 0, 2)))
        
        # ✅ Escalamientos
        total_escaladas = novedades.filter(esta_escalada=True).count()
        porcentaje_escaladas = Decimal(str(round((total_escaladas / total * 100) if total > 0 else 0, 2)))
        
        # ✅ Crear registro de métrica
        metrica = cls.objects.create(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_novedades=total,
            novedades_resueltas=resueltas,
            novedades_pendientes=pendientes,
            novedades_canceladas=canceladas,
            severidad_bajo=severidades['BAJO'],
            severidad_medio=severidades['MEDIO'],
            severidad_alto=severidades['ALTO'],
            severidad_critico=severidades['CRITICO'],
            severidad_emergencia=severidades['EMERGENCIA'],
            sla_cumplido=sla_cumplido,
            sla_vencido=sla_vencido,
            porcentaje_cumplimiento_sla=porcentaje_sla,
            tiempo_promedio_respuesta_horas=avg_respuesta,
            tiempo_promedio_resolucion_horas=avg_resolucion,
            impacto_economico_total=impacto_total,
            clientes_afectados_total=clientes_afectados,
            total_acciones=total_acciones,
            acciones_efectivas=acciones_efectivas,
            porcentaje_efectividad=porcentaje_efectividad,
            total_escaladas=total_escaladas,
            porcentaje_escaladas=porcentaje_escaladas,
        )
        
        return metrica
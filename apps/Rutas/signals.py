from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Ruta, ParadaRuta, AsignacionVehiculo, AsignacionConductor, MetricaRuta


@receiver(post_save, sender=Ruta)
def crear_metricas_al_completar_ruta(sender, instance, created, **kwargs):
    """
    Crea automáticamente las métricas cuando una ruta se completa.
    """
    if not created and instance.estado == 'COMPLETADA':
        # ✅ Verificar si ya existen métricas
        if not hasattr(instance, 'metricas'):
            MetricaRuta.objects.create(
                ruta=instance,
                distancia_planificada_km=instance.distancia_total_km,
                distancia_real_km=instance.distancia_total_km,  # ✅ Calcular real
                tiempo_planificado_minutos=instance.tiempo_estimado_minutos,
                tiempo_real_minutos=instance.tiempo_real_minutos or 0,
                total_paradas_planificadas=instance.total_paradas,
                total_paradas_completadas=instance.paradas_completadas,
                combustible_planificado_litros=instance.combustible_estimado_litros,
                combustible_real_litros=instance.combustible_real_litros,
                costo_planificado=instance.costo_estimado,
                costo_real=instance.costo_real,
            )


@receiver(post_save, sender=AsignacionVehiculo)
def actualizar_estado_vehiculo(sender, instance, created, **kwargs):
    """
    Actualiza el estado del vehículo cuando se asigna/remueve de una ruta.
    """
    if created and instance.fecha_fin is None:
        # ✅ Nueva asignación
        instance.vehiculo.estado = 'RESERVADO'
        instance.vehiculo.save()
    
    if instance.fecha_fin and not created:
        # ✅ Remoción de asignación
        instance.vehiculo.estado = 'DISPONIBLE'
        instance.vehiculo.save()


@receiver(post_save, sender=ParadaRuta)
def actualizar_estado_ruta(sender, instance, **kwargs):
    """
    Actualiza el estado de la ruta basado en el estado de las paradas.
    """
    ruta = instance.ruta
    
    if ruta.estado == 'EN_CURSO':
        paradas_totales = ruta.paradas.count()
        paradas_completadas = ruta.paradas.filter(estado='COMPLETADA').count()
        
        if paradas_completadas == paradas_totales and paradas_totales > 0:
            # ✅ Todas las paradas completadas
            ruta.estado = 'COMPLETADA'
            ruta.save()
        
        elif paradas_completadas > 0:
            # ✅ Algunas paradas completadas
            ruta.estado = 'PARCIALMENTE_COMPLETADA'
            ruta.save()
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Pedido, GuiaEnvio, EventoTracking, PruebaEntrega, NotificacionEnvio
from .models.choices import TipoEventoTracking, TipoNotificacion


@receiver(post_save, sender=Pedido)
def notificar_cambio_estado_pedido(sender, instance, created, **kwargs):
    """Enviar notificación cuando cambia el estado del pedido"""
    if created:
        # ✅ Notificación de pedido creado
        NotificacionEnvio.objects.create(
            pedido=instance,
            tipo=TipoNotificacion.EMAIL,
            evento_trigger='PEDIDO_CREADO',
            destinatario_email=instance.usuario.email,
            destinatario_usuario=instance.usuario,
            asunto=f'Pedido {instance.numero_pedido} creado',
            mensaje=f'Su pedido ha sido creado exitosamente. Código de rastreo: {instance.codigo_rastreo}',
            plantilla='pedido_creado',
        )
    else:
        # ✅ Notificación de cambio de estado
        NotificacionEnvio.objects.create(
            pedido=instance,
            tipo=TipoNotificacion.EMAIL,
            evento_trigger='CAMBIO_ESTADO',
            destinatario_email=instance.usuario.email,
            destinatario_usuario=instance.usuario,
            asunto=f'Pedido {instance.numero_pedido} - {instance.get_estado_display()}',
            mensaje=f'El estado de su pedido ha cambiado a: {instance.get_estado_display()}',
            plantilla='cambio_estado_pedido',
        )


@receiver(post_save, sender=GuiaEnvio)
def notificar_guia_generada(sender, instance, created, **kwargs):
    """Enviar notificación cuando se genera una guía"""
    if created:
        NotificacionEnvio.objects.create(
            pedido=instance.pedido,
            tipo=TipoNotificacion.EMAIL,
            evento_trigger='GUIA_GENERADA',
            destinatario_email=instance.pedido.usuario.email,
            destinatario_usuario=instance.pedido.usuario,
            asunto=f'Guía {instance.numero_guia} generada',
            mensaje=f'Su guía de envío ha sido generada. Número: {instance.numero_guia}',
            plantilla='guia_generada',
        )


@receiver(post_save, sender=PruebaEntrega)
def notificar_entrega_completada(sender, instance, created, **kwargs):
    """Enviar notificación cuando se completa la entrega"""
    if created:
        # ✅ Notificar al cliente
        NotificacionEnvio.objects.create(
            pedido=instance.pedido,
            tipo=TipoNotificacion.EMAIL,
            evento_trigger='ENTREGA_COMPLETADA',
            destinatario_email=instance.pedido.usuario.email,
            destinatario_usuario=instance.pedido.usuario,
            asunto=f'Pedido {instance.pedido.numero_pedido} entregado',
            mensaje=f'Su pedido ha sido entregado exitosamente. Recibido por: {instance.nombre_recibidor}',
            plantilla='entrega_completada',
        )
        
        # ✅ Actualizar estado del pedido
        instance.pedido.estado = 'ENTREGADO'
        instance.pedido.fecha_entrega_real = instance.fecha_entrega
        instance.pedido.save()
        
        # ✅ Cerrar guía
        if hasattr(instance.pedido, 'guia'):
            instance.pedido.guia.cerrar_guia()


@receiver(post_save, sender=EventoTracking)
def actualizar_estado_pedido(sender, instance, created, **kwargs):
    """Actualizar estado del pedido basado en evento de tracking"""
    # ✅ Esta lógica ya está en el modelo EventoTracking.save()
    # Pero se puede reforzar aquí si es necesario
    pass
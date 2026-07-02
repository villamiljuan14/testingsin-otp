from django.db import models
from .choices import TipoNotificacion
from .pedido import Pedido


class NotificacionEnvio(models.Model):
    """
    Sistema de notificaciones por evento.
    Similar a FedEx Delivery Manager.
    """
    # ✅ Relación con pedido
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    
    # ✅ Tipo de notificación
    tipo = models.CharField(
        max_length=20,
        choices=TipoNotificacion.choices
    )
    
    # ✅ Evento que dispara la notificación
    evento_trigger = models.CharField(
        max_length=50,
        help_text='Evento que generó esta notificación'
    )
    
    # ✅ Destinatario
    destinatario_email = models.EmailField(null=True, blank=True)
    destinatario_telefono = models.CharField(max_length=20, null=True, blank=True)
    destinatario_usuario = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # ✅ Contenido
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    plantilla = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Nombre de la plantilla usada'
    )
    
    # ✅ Estado de envío
    estado = models.CharField(
        max_length=30,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ENVIADA', 'Enviada'),
            ('ENTREGADA', 'Entregada'),
            ('FALLIDA', 'Fallida'),
            ('REBOTADA', 'Rebotada'),
        ],
        default='PENDIENTE'
    )
    
    # ✅ Intentos
    intentos_envio = models.PositiveIntegerField(default=0)
    max_intentos = models.PositiveIntegerField(default=3)
    
    # ✅ Fechas
    fecha_programada = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    # ✅ Errores
    error_mensaje = models.TextField(null=True, blank=True)
    
    # ✅ Tracking externo
    id_externo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='ID del proveedor de email/SMS'
    )
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_notificacion_envio'
        verbose_name = 'Notificación de Envío'
        verbose_name_plural = 'Notificaciones de Envío'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['pedido', 'estado']),
            models.Index(fields=['estado', 'fecha_programada']),
            models.Index(fields=['destinatario_usuario', 'estado']),
        ]
    
    def __str__(self):
        return f'Notificación {self.id} - {self.pedido.numero_pedido} - {self.estado}'
    
    def marcar_enviada(self, id_externo=None):
        """Marca la notificación como enviada"""
        from django.utils import timezone
        self.estado = 'ENVIADA'
        self.fecha_envio = timezone.now()
        self.id_externo = id_externo
        self.save()
    
    def marcar_entregada(self):
        """Marca la notificación como entregada"""
        from django.utils import timezone
        self.estado = 'ENTREGADA'
        self.fecha_entrega = timezone.now()
        self.save()
    
    def marcar_fallida(self, error):
        """Marca la notificación como fallida"""
        self.estado = 'FALLIDA'
        self.error_mensaje = error
        self.intentos_envio += 1
        self.save()
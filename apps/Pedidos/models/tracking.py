from django.db import models
# from django.contrib.gis.db import models as gismodels  # ❌ Temporalmente desactivado
from .choices import TipoEventoTracking
from .pedido import Pedido
from .hub import Hub


from django.core.validators import FileExtensionValidator

class EventoTracking(models.Model):
    """
    Eventos de tracking granulares - Cada escaneo es un evento.
    Similar al tracking detallado de FedEx.
    """
    # ✅ Relación con pedido
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='eventos_tracking'
    )
    guia = models.ForeignKey(
        'GuiaEnvio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='eventos_tracking'
    )
    
    # ✅ Tipo de evento
    tipo_evento = models.CharField(
        max_length=50,
        choices=TipoEventoTracking.choices
    )
    
    # ✅ Ubicación del evento
    hub = models.ForeignKey(
        Hub,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_tracking',
        help_text='Hub donde ocurrió el evento'
    )
    ubicacion_texto = models.CharField(
        max_length=255,
        help_text='Ciudad, instalación o coordenadas'
    )
    
    # ✅ Geolocalización (para eventos en ruta)
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # ✅ Detalles
    descripcion = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    # ✅ Responsable del escaneo
    registrado_por = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_registrados'
    )
    
    # ✅ Fecha y hora
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # ✅ Evidencia (fotos, firmas, etc.)
    evidencia_foto = models.ImageField(
        upload_to='tracking/evidencias/',
        null=True,
        blank=True
    )
    evidencia_documento = models.FileField(
        upload_to='tracking/documentos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt'])]
    )
    
    class Meta:
        db_table = 'pedidos_evento_tracking'
        verbose_name = 'Evento de Tracking'
        verbose_name_plural = 'Eventos de Tracking'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['pedido', 'fecha_registro']),
            models.Index(fields=['tipo_evento', 'fecha_registro']),
            models.Index(fields=['hub', 'fecha_registro']),
        ]
    
    def __str__(self):
        return f'{self.pedido.numero_pedido} - {self.get_tipo_evento_display()} ({self.fecha_registro})'
    
    def save(self, *args, **kwargs):
        """Actualiza el estado del pedido automáticamente"""
        super().save(*args, **kwargs)
        
        # ✅ Mapeo de evento a estado del pedido
        estado_mapping = {
            TipoEventoTracking.PEDIDO_CONFIRMADO: 'CONFIRMADO',
            TipoEventoTracking.RECOLECTADO: 'RECOLECTADO',
            TipoEventoTracking.LLEGADA_HUB_ORIGEN: 'EN_HUB_ORIGEN',
            TipoEventoTracking.SALIDA_HUB_ORIGEN: 'EN_TRANSITO',
            TipoEventoTracking.LLEGADA_HUB_DESTINO: 'EN_HUB_DESTINO',
            TipoEventoTracking.SALIDA_HUB_DESTINO: 'EN_REPARTO',
            TipoEventoTracking.EN_REPARTO: 'EN_REPARTO',
            TipoEventoTracking.ENTREGADO: 'ENTREGADO',
            TipoEventoTracking.DEVUELTO_REMITENTE: 'DEVUELTO',
            TipoEventoTracking.CANCELADO: 'CANCELADO',
        }
        
        if self.tipo_evento in estado_mapping:
            self.pedido.estado = estado_mapping[self.tipo_evento]
            
            # ✅ Si es entregado, guardar fecha real
            if self.tipo_evento == TipoEventoTracking.ENTREGADO:
                self.pedido.fecha_entrega_real = self.fecha_registro
            
            self.pedido.save(update_fields=['estado', 'fecha_entrega_real'])
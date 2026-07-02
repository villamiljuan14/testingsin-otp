from django.db import models
# from django.contrib.gis.db import models as gismodels  # ❌ Temporalmente desactivado
from decimal import Decimal
from .pedido import Pedido


from django.core.validators import FileExtensionValidator

class PruebaEntrega(models.Model):
    """
    Proof of Delivery (POD) - Evidencia legal de entrega.
    Crítico para reclamos y validación de servicio.
    """
    # ✅ Relación con pedido
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.PROTECT,
        related_name='prueba_entrega'
    )
    
    # ✅ Datos del recibidor
    nombre_recibidor = models.CharField(max_length=100)
    documento_recibidor = models.CharField(max_length=50, null=True, blank=True)
    relacion_destinatario = models.CharField(
        max_length=50,
        choices=[
            ('DESTINATARIO', 'Destinatario directo'),
            ('FAMILIAR', 'Familiar'),
            ('VECINO', 'Vecino'),
            ('SEGURIDAD', 'Seguridad/Recepción'),
            ('OTRO', 'Otro'),
        ],
        default='DESTINATARIO'
    )
    telefono_recibidor = models.CharField(max_length=20, null=True, blank=True)
    
    # ✅ Firma digital
    firma_digitizada = models.ImageField(
        upload_to='pod/firmas/',
        help_text='Firma capturada en dispositivo móvil',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]
    )
    
    # ✅ Evidencia fotográfica
    foto_paquete = models.ImageField(
        upload_to='pod/fotos/paquete/',
        help_text='Foto del paquete en lugar de entrega',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    foto_frente = models.ImageField(
        upload_to='pod/fotos/frente/',
        null=True,
        blank=True,
        help_text='Foto del frente del inmueble (opcional)',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    fotos_adicionales = models.JSONField(
        null=True,
        blank=True,
        help_text='URLs de fotos adicionales'
    )
    
    # ✅ Geolocalización exacta de entrega
    latitud_entrega = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Latitud GPS del punto de entrega'
    )
    longitud_entrega = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Longitud GPS del punto de entrega'
    )
    precision_gps = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precisión del GPS en metros'
    )
    
    # ✅ Fecha y hora
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    
    # ✅ Mensajero que entregó
    mensajero = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.PROTECT,
        related_name='entregas_realizadas',
        limit_choices_to={'rol__tipo_rol': 'MENSAJERO'}
    )
    
    # ✅ Observaciones
    observaciones = models.TextField(null=True, blank=True)
    condiciones_entrega = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Estado del paquete al entregar (ej: sin daños)'
    )
    
    # ✅ Validación
    es_validada = models.BooleanField(default=False)
    validada_por = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pod_validados'
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_prueba_entrega'
        verbose_name = 'Prueba de Entrega (POD)'
        verbose_name_plural = 'Pruebas de Entrega (POD)'
        ordering = ['-fecha_entrega']
        indexes = [
            models.Index(fields=['pedido']),
            models.Index(fields=['mensajero', 'fecha_entrega']),
            models.Index(fields=['fecha_entrega']),
        ]
    
    def __str__(self):
        return f'POD - {self.pedido.numero_pedido} - {self.nombre_recibidor}'
    
    def save(self, *args, **kwargs):
        """Override save para cambiar estado del pedido a ENTREGADO automáticamente"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Cambiar estado del pedido a ENTREGADO cuando se crea la prueba de entrega
        if is_new and self.pedido:
            from .choices import EstadoPedido
            from django.utils import timezone
            self.pedido.estado = EstadoPedido.ENTREGADO
            self.pedido.fecha_entrega_real = timezone.now()
            self.pedido.save()
            
            # Crear evento de tracking
            from .tracking import EventoTracking, TipoEventoTracking
            EventoTracking.objects.create(
                pedido=self.pedido,
                tipo_evento=TipoEventoTracking.ENTREGADO,
                ubicacion_texto=f'{self.latitud_entrega}, {self.longitud_entrega}',
                registrado_por=self.mensajero,
                descripcion=f'Entrega completada. Recibido por: {self.nombre_recibidor}'
            )
    
    def validar_pod(self, usuario_validador):
        """Valida la prueba de entrega"""
        from django.utils import timezone
        self.es_validada = True
        self.validada_por = usuario_validador
        self.fecha_validacion = timezone.now()
        self.save()
    
    def calcular_distancia_desde_hub(self):
        """Calcula distancia entre hub de destino y punto de entrega"""
        if self.pedido.hub_destino and self.pedido.hub_destino.latitud:
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lat1, lon1, lat2, lon2):
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                return km
            
            return haversine(
                float(self.pedido.hub_destino.latitud),
                float(self.pedido.hub_destino.longitud),
                float(self.latitud_entrega),
                float(self.longitud_entrega)
            )
        return None
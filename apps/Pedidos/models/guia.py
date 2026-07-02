from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .choices import EstadoGuia
from .pedido import Pedido


from django.core.validators import FileExtensionValidator

class GuiaEnvio(models.Model):
    """
    Guía de envío - Documento legal del transporte.
    Similar a la guía aérea o bill of lading de FedEx.
    """
    # ✅ Identificación única
    numero_guia = models.CharField(max_length=50, unique=True, db_index=True, editable=False)
    codigo_barras = models.CharField(max_length=100, unique=True, help_text='Código de barras para escaneo')
    codigo_qr = models.CharField(max_length=255, null=True, blank=True, help_text='QR para tracking móvil')
    
    # ✅ Relación con pedido
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='guia'
    )
    
    # ✅ Estado
    estado = models.CharField(
        max_length=30,
        choices=EstadoGuia.choices,
        default=EstadoGuia.GENERADA
    )
    
    # ✅ Fechas
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_impresion = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    # ✅ Dimensiones y peso (validación al momento de generar guía)
    peso_final_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    dimensiones = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Formato: LxAxAl cm (ej: 20x30x15)'
    )
    
    # ✅ Archivos
    archivo_pdf = models.FileField(
        upload_to='guias/pdfs/',
        null=True,
        blank=True,
        help_text='PDF de la guía para descarga',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    etiqueta_path = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Ruta de la etiqueta en almacenamiento'
    )
    
    # ✅ Instrucciones especiales
    instrucciones_especiales = models.TextField(null=True, blank=True)
    es_fragil = models.BooleanField(default=False)
    requiere_firma = models.BooleanField(default=True)
    no_doblar = models.BooleanField(default=False)
    
    # ✅ Auditoría
    generada_por = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='guias_generadas'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_guia_envio'
        verbose_name = 'Guía de Envío'
        verbose_name_plural = 'Guías de Envío'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['numero_guia']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['estado', 'fecha_generacion']),
        ]
    
    def __str__(self):
        return f'Guía {self.numero_guia} - Pedido {self.pedido.numero_pedido}'
    
    def save(self, *args, **kwargs):
        """Genera número de guía automático"""
        if not self.numero_guia:
            from django.utils import timezone
            year = timezone.now().year
            last_guia = GuiaEnvio.objects.filter(
                numero_guia__startswith=f'GUI-{year}-'
            ).order_by('-numero_guia').first()
            
            if last_guia:
                last_num = int(last_guia.numero_guia.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.numero_guia = f'GUI-{year}-{new_num:06d}'
        
        # ✅ Generar código de barras (simplificado, en producción usar librería)
        if not self.codigo_barras:
            import secrets
            self.codigo_barras = secrets.token_hex(16).upper()
        
        # ✅ Sincronizar peso con pedido
        if not self.peso_final_kg:
            self.peso_final_kg = self.pedido.peso_cobrar
        
        super().save(*args, **kwargs)
    
    def marcar_impresa(self):
        """Marca la guía como impresa"""
        from django.utils import timezone
        self.estado = EstadoGuia.IMPRESA
        self.fecha_impresion = timezone.now()
        self.save()
    
    def marcar_en_circulacion(self):
        """Marca la guía como en circulación"""
        self.estado = EstadoGuia.EN_CIRCULACION
        self.save()
    
    def cerrar_guia(self):
        """Cierra la guía (entrega completada)"""
        from django.utils import timezone
        self.estado = EstadoGuia.CERRADA
        self.fecha_cierre = timezone.now()
        self.save()
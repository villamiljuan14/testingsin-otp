from django.db import models
from django.conf import settings
from .choices import TipoEvidencia
from .novedad import Novedad


from django.core.validators import FileExtensionValidator

class EvidenciaNovedad(models.Model):
    """
    Evidencia adjunta a novedades (fotos, videos, documentos).
    4NF: Entidad separada para relación 1:N con Novedad.
    """
    novedad = models.ForeignKey(
        Novedad,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )
    
    # ✅ Tipo de evidencia
    tipo = models.CharField(
        max_length=20,
        choices=TipoEvidencia.choices,
        default=TipoEvidencia.FOTO
    )
    
    # ✅ Archivo
    archivo = models.FileField(
        upload_to='novedades/evidencias/%Y/%m/%d/',
        max_length=255,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'pdf', 'doc', 'docx', 'mp4'])]
    )
    nombre_original = models.CharField(max_length=255, null=True, blank=True)
    tamaño_bytes = models.PositiveIntegerField(null=True, blank=True)
    contenido_type = models.CharField(max_length=100, null=True, blank=True)
    
    # ✅ Descripción
    descripcion = models.TextField(null=True, blank=True)
    
    # ✅ Ubicación donde se capturó
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_captura = models.DateTimeField(null=True, blank=True)
    
    # ✅ Auditoría
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evidencias_subidas'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'novedades_evidencia'
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['novedad', 'tipo']),
            models.Index(fields=['subido_por', 'creado_en']),
        ]
    
    def __str__(self):
        return f'Evidencia {self.id} - {self.get_tipo_display()}'
    
    def save(self, *args, **kwargs):
        """Calcula tamaño del archivo automáticamente"""
        if self.archivo:
            try:
                self.tamaño_bytes = self.archivo.size
                self.nombre_original = self.archivo.name.split('/')[-1]
            except:
                pass
        super().save(*args, **kwargs)
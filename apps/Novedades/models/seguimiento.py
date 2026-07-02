from django.db import models
from django.conf import settings
from .novedad import Novedad


class SeguimientoNovedad(models.Model):
    """
    Historial de cambios y seguimiento de novedades.
    4NF: Entidad separada para auditoría completa.
    """
    novedad = models.ForeignKey(
        Novedad,
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    
    # ✅ Campo cambiado
    campo_cambiado = models.CharField(max_length=100)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo = models.TextField(null=True, blank=True)
    
    # ✅ Usuario que hizo el cambio
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seguimientos_novedades'
    )
    
    # ✅ Contexto
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    # ✅ Timestamp
    fecha_cambio = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'novedades_seguimiento'
        verbose_name = 'Seguimiento de Novedad'
        verbose_name_plural = 'Seguimientos de Novedades'
        ordering = ['-fecha_cambio']
        indexes = [
            models.Index(fields=['novedad', 'fecha_cambio']),
            models.Index(fields=['usuario', 'fecha_cambio']),
            models.Index(fields=['campo_cambiado']),
        ]
    
    def __str__(self):
        return f'{self.novedad.codigo_novedad} - {self.campo_cambiado} ({self.fecha_cambio})'
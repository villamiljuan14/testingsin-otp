from django.db import models
from .departamento import Departamento


class Ciudad(models.Model):
    """
    Ciudades/municipios por departamento.
    """
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='ciudades'
    )
    nombre = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    es_capital = models.BooleanField(default=False)
    es_activo = models.BooleanField(default=True)
    
    # ✅ Para cálculo de zonas de envío
    zona_envio = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Zona para tarifación (ej: ZONA1, ZONA2)'
    )
    
    class Meta:
        db_table = 'ubicaciones_ciudad'
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['departamento', 'nombre']
        unique_together = ['departamento', 'nombre']
        indexes = [
            models.Index(fields=['departamento', 'es_activo']),
            models.Index(fields=['zona_envio']),
        ]
    
    def __str__(self):
        return f'{self.nombre}, {self.departamento.nombre}'
    
    @property
    def nombre_completo(self):
        return f'{self.nombre}, {self.departamento.nombre}, {self.departamento.pais.nombre}'
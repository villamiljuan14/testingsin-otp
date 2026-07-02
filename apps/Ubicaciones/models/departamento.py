from django.db import models
from .pais import Pais


class Departamento(models.Model):
    """
    Departamentos/Estados/Provincias por país.
    """
    pais = models.ForeignKey(
        Pais,
        on_delete=models.CASCADE,
        related_name='departamentos'
    )
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, null=True, blank=True, help_text='Código interno')
    codigo_iso = models.CharField(max_length=10, null=True, blank=True, help_text='Código ISO 3166-2')
    capital = models.CharField(max_length=100, null=True, blank=True)
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ubicaciones_departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['pais', 'nombre']
        unique_together = ['pais', 'nombre']
        indexes = [
            models.Index(fields=['pais', 'es_activo']),
        ]
    
    def __str__(self):
        return f'{self.nombre} ({self.pais.codigo_iso2})'
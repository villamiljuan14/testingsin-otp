from django.db import models


class Pais(models.Model):
    """
    Catálogo de países para normalización de direcciones.
    """
    nombre = models.CharField(max_length=100, unique=True)
    nombre_corto = models.CharField(max_length=50, help_text='Nombre común')
    codigo_iso2 = models.CharField(max_length=2, unique=True, help_text='Código ISO 3166-1 alpha-2')
    codigo_iso3 = models.CharField(max_length=3, unique=True, help_text='Código ISO 3166-1 alpha-3')
    codigo_telefono = models.CharField(max_length=10, help_text='Ej: +57 para Colombia')
    moneda = models.CharField(max_length=3, default='COP', help_text='Código ISO 4217')
    requiere_departamento = models.BooleanField(default=True, help_text='¿Requiere estado/departamento?')
    requiere_codigo_postal = models.BooleanField(default=True)
    es_activo = models.BooleanField(default=True)
    
    # ✅ Para integración con APIs externas
    codigo_tributario = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        db_table = 'ubicaciones_pais'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_iso2']),
            models.Index(fields=['es_activo']),
        ]
    
    def __str__(self):
        return f'{self.nombre} ({self.codigo_iso2})'
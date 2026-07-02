from django.db import models
# from django.contrib.gis.db import models as gismodels  # ❌ Temporalmente desactivado para migración


class Hub(models.Model):
    """
    Centros de distribución tipo FedEx.
    Permite gestionar la red logística de hubs.
    """
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, db_index=True)  # Ej: BOG-HUB-01
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('CENTRAL', 'Hub Central'),
            ('REGIONAL', 'Hub Regional'),
            ('LOCAL', 'Hub Local'),
            ('PUNTO_ENTREGA', 'Punto de Entrega'),
        ]
    )
    
    # ✅ Ubicación geográfica (requiere PostGIS para producción)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Colombia')
    codigo_postal = models.CharField(max_length=20)
    
    # ✅ Coordenadas para cálculos de ruta
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # ✅ Operación
    telefono = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fin = models.TimeField(null=True, blank=True)
    es_activo = models.BooleanField(default=True)
    
    # ✅ Relaciones
    hub_padre = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hubs_hijos',
        help_text='Hub regional al que pertenece (para hubs locales)'
    )
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_hub'
        verbose_name = 'Hub de Distribución'
        verbose_name_plural = 'Hubs de Distribución'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo', 'es_activo']),
            models.Index(fields=['ciudad', 'departamento']),
        ]
    
    def __str__(self):
        return f'{self.codigo} - {self.nombre}'
    
    @property
    def es_hub_central(self):
        return self.tipo == 'CENTRAL'
    
    def get_hijos_recursivo(self):
        """Obtiene todos los hubs hijos de forma recursiva"""
        hijos = list(self.hubs_hijos.all())
        for hijo in self.hubs_hijos.all():
            hijos.extend(hijo.get_hijos_recursivo())
        return hijos
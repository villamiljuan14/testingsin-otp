from django.db import models
from django.conf import settings


class CategoriaNovedad(models.Model):
    """
    Categorización de novedades para clasificación y reporting.
    Permite agrupar novedades similares para análisis.
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    descripcion = models.TextField(null=True, blank=True)
    
    # ✅ Jerarquía de categorías
    categoria_padre = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    
    # ✅ Configuración
    tipo_novedad = models.CharField(
        max_length=30,
        choices=[(t.value, t.label) for t in __import__('apps.Novedades.models.choices', fromlist=['TipoNovedad']).TipoNovedad],
        null=True,
        blank=True
    )
    severidad_default = models.CharField(
        max_length=20,
        choices=[(s.value, s.label) for s in __import__('apps.Novedades.models.choices', fromlist=['SeveridadNovedad']).SeveridadNovedad],
        default='MEDIO'
    )
    
    # ✅ SLA por categoría
    sla_horas_respuesta = models.PositiveIntegerField(default=24)
    sla_horas_resolucion = models.PositiveIntegerField(default=72)
    
    # ✅ Asignación automática
    equipo_responsable = models.CharField(max_length=100, null=True, blank=True)
    requiere_aprobacion = models.BooleanField(default=False)
    nivel_aprobacion_requerido = models.PositiveIntegerField(default=1)
    
    # ✅ Estado
    es_activa = models.BooleanField(default=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'novedades_categoria'
        verbose_name = 'Categoría de Novedad'
        verbose_name_plural = 'Categorías de Novedades'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo', 'es_activa']),
            models.Index(fields=['categoria_padre', 'es_activa']),
        ]
    
    def __str__(self):
        return f'{self.nombre} ({self.codigo})'
    
    @property
    def nombre_completo(self):
        """Retorna nombre con jerarquía completa"""
        if self.categoria_padre:
            return f'{self.categoria_padre.nombre} > {self.nombre}'
        return self.nombre
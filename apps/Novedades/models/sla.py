from django.db import models
from django.conf import settings
from .categoria import CategoriaNovedad


class SLANovedad(models.Model):
    """
    Configuración de SLA (Service Level Agreement) para novedades.
    Define tiempos máximos de respuesta y resolución por categoría/severidad.
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    
    # ✅ Categoría aplicable
    categoria = models.ForeignKey(
        CategoriaNovedad,
        on_delete=models.CASCADE,
        related_name='slas',
        null=True,
        blank=True
    )
    
    # ✅ Severidad aplicable
    severidad = models.CharField(
        max_length=20,
        choices=[(s.value, s.label) for s in __import__('apps.Novedades.models.choices', fromlist=['SeveridadNovedad']).SeveridadNovedad],
        null=True,
        blank=True
    )
    
    # ✅ Tiempos SLA
    tiempo_respuesta_horas = models.PositiveIntegerField(help_text='Horas máximas para primera respuesta')
    tiempo_resolucion_horas = models.PositiveIntegerField(help_text='Horas máximas para resolución')
    
    # ✅ Horario de aplicación
    aplica_24_7 = models.BooleanField(default=True)
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fin = models.TimeField(null=True, blank=True)
    dias_semana = models.CharField(
        max_length=50,
        default='1,2,3,4,5',
        help_text='Días de semana (1=Lunes, 7=Domingo)'
    )
    
    # ✅ Escalamiento automático
    escalar_antes_vencimiento = models.BooleanField(default=True)
    horas_antes_escalamiento = models.PositiveIntegerField(default=2)
    nivel_escalamiento_automatico = models.PositiveIntegerField(default=1)
    
    # ✅ Notificaciones
    notificar_vencimiento = models.BooleanField(default=True)
    horas_antes_notificacion = models.PositiveIntegerField(default=4)
    
    # ✅ Estado
    es_activo = models.BooleanField(default=True)
    fecha_inicio_vigencia = models.DateField(null=True, blank=True)
    fecha_fin_vigencia = models.DateField(null=True, blank=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'novedades_sla'
        verbose_name = 'SLA de Novedad'
        verbose_name_plural = 'SLAs de Novedades'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['categoria', 'severidad', 'es_activo']),
            models.Index(fields=['es_activo', 'fecha_inicio_vigencia']),
        ]
    
    def __str__(self):
        return f'{self.nombre} - {self.tiempo_respuesta_horas}h/{self.tiempo_resolucion_horas}h'
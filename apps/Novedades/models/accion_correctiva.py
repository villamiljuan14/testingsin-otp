from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from .choices import TipoAccion
from .novedad import Novedad


class AccionCorrectiva(models.Model):
    """
    Acciones correctivas para resolver novedades.
    4NF: Entidad separada para relación 1:N con Novedad.
    """
    novedad = models.ForeignKey(
        Novedad,
        on_delete=models.CASCADE,
        related_name='acciones_correctivas'
    )
    
    # ✅ Tipo de acción
    tipo = models.CharField(
        max_length=30,
        choices=TipoAccion.choices,
        default=TipoAccion.CORRECTIVA
    )
    
    # ✅ Descripción
    descripcion = models.TextField(help_text='Descripción detallada de la acción')
    
    # ✅ Responsable
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_correctivas_responsable'
    )
    
    # ✅ Fechas
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    # ✅ Estado
    estado = models.CharField(
        max_length=30,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('EN_PROGRESO', 'En Progreso'),
            ('COMPLETADA', 'Completada'),
            ('CANCELADA', 'Cancelada'),
        ],
        default='PENDIENTE',
        db_index=True
    )
    
    # ✅ Costos
    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    costo_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # ✅ Resultados
    resultados = models.TextField(null=True, blank=True)
    efectiva = models.BooleanField(null=True, blank=True)
    
    # ✅ Verificación
    verificada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_verificadas'
    )
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'novedades_accion_correctiva'
        verbose_name = 'Acción Correctiva'
        verbose_name_plural = 'Acciones Correctivas'
        ordering = ['-fecha_asignacion']
        indexes = [
            models.Index(fields=['novedad', 'estado']),
            models.Index(fields=['responsable', 'estado']),
            models.Index(fields=['fecha_limite', 'estado']),
        ]
    
    def __str__(self):
        return f'Acción {self.id} - {self.get_tipo_display()}'
    
    def iniciar_accion(self, usuario):
        """Inicia la acción correctiva"""
        from django.utils import timezone
        self.estado = 'EN_PROGRESO'
        self.fecha_inicio = timezone.now()
        self.save()
    
    def completar_accion(self, resultados, usuario):
        """Completa la acción correctiva"""
        from django.utils import timezone
        self.estado = 'COMPLETADA'
        self.fecha_completado = timezone.now()
        self.resultados = resultados
        self.save()
    
    def verificar_accion(self, efectiva, usuario):
        """Verifica la acción correctiva"""
        from django.utils import timezone
        self.efectiva = efectiva
        self.verificada_por = usuario
        self.fecha_verificacion = timezone.now()
        self.save()
from django.db import models
from .ciudad import Ciudad


class Hub(models.Model):
    """
    Modelo de Hubs/Puntos de Distribución
    Centros logísticos del sistema
    """
    TIPO_HUB_CHOICES = [
        ('PRINCIPAL', 'Hub Principal'),
        ('SECUNDARIO', 'Hub Secundario'),
        ('TEMPORAL', 'Hub Temporal'),
        ('PARTNER', 'Hub de Partner'),
    ]

    nombre = models.CharField(
        max_length=100,
        unique=True
    )
    codigo_hub = models.CharField(
        max_length=10,
        unique=True,
        help_text='Código único del hub'
    )
    tipo_hub = models.CharField(
        max_length=20,
        choices=TIPO_HUB_CHOICES,
        default='PRINCIPAL'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        related_name='hubs'
    )
    direccion = models.CharField(
        max_length=200,
        help_text='Dirección completa del hub'
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    email_contacto = models.EmailField(
        null=True,
        blank=True
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    capacidad_operativa = models.PositiveIntegerField(
        default=1000,
        help_text='Capacidad operativa diaria (paquetes)'
    )
    horario_operacion = models.CharField(
        max_length=100,
        default='08:00-18:00',
        help_text='Horario de operación'
    )
    servicios_disponibles = models.JSONField(
        default=dict,
        help_text='Servicios disponibles en el hub'
    )
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hubs'
        verbose_name = 'Hub'
        verbose_name_plural = 'Hubs'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_hub']),
            models.Index(fields=['ciudad']),
            models.Index(fields=['tipo_hub']),
            models.Index(fields=['es_activo']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.codigo_hub})'

    @property
    def direccion_completa(self):
        """Retorna dirección completa con ciudad"""
        if self.ciudad:
            return f'{self.direccion}, {self.ciudad.nombre}'
        return self.direccion

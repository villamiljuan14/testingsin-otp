from django.db import models
from django.conf import settings


class TipoNovedad(models.TextChoices):
    ACTUALIZACION = 'ACTUALIZACION', 'Actualización'
    INCIDENCIA = 'INCIDENCIA', 'Incidencia'
    ENTREGA = 'ENTREGA', 'Entrega'
    OTRO = 'OTRO', 'Otro'


class NovedadPedido(models.Model):
    pedido = models.ForeignKey(
        'Pedidos.Pedido',  
        on_delete=models.PROTECT,
        related_name='novedades'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='novedades_creadas',
        help_text='Usuario que registró la novedad'
    )
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_novedad = models.DateTimeField()
    tipo_novedad = models.CharField(max_length=30, choices=TipoNovedad.choices)

    class Meta:
        db_table = 'novedad_pedido'
        verbose_name = 'Novedad de Pedido'
        verbose_name_plural = 'Novedades de Pedido'
        ordering = ['-fecha_novedad']

    def __str__(self):
        return f'{self.titulo} - {self.tipo_novedad}'

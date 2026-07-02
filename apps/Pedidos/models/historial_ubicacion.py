from django.db import models

from .pedido import Pedido


class HistorialUbicacion(models.Model):
    """Pings GPS en vivo enviados por el mensajero durante la entrega."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historial_ubicaciones',
    )
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    precision_gps = models.FloatField(null=True, blank=True)
    registrado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'pedidos_historial_ubicacion'
        verbose_name = 'Historial de ubicación'
        verbose_name_plural = 'Historial de ubicaciones'
        ordering = ['registrado_en']
        indexes = [
            models.Index(fields=['pedido', 'registrado_en']),
        ]

    def __str__(self):
        return f'Pedido #{self.pedido_id} ({self.latitud}, {self.longitud})'

from django.db import models
from django.conf import settings
from .pedido import Pedido

class Pago(models.Model):
    class MetodoPago(models.TextChoices):
        TARJETA = 'TARJETA_CREDITO', 'Tarjeta de Crédito'
        PSE = 'PSE', 'PSE / Cuenta de Ahorros'
        NEQUI = 'NEQUI', 'Nequi'
        BANCOLOMBIA = 'BANCOLOMBIA_TRANSFER', 'Transferencia Bancolombia'
        EFECTIVO = 'EFECTIVO', 'Efectivo / Corresponsal'

    class EstadoPago(models.TextChoices):
        APROBADO = 'APPROVED', 'Aprobado'
        DECLINADO = 'DECLINED', 'Declinado'
        ERROR = 'ERROR', 'Error en Transacción'
        PENDIENTE = 'PENDING', 'Pendiente'

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    wompi_tx_id = models.CharField(max_length=100, unique=True, verbose_name="ID de Transacción Wompi")
    metodo = models.CharField(max_length=30, choices=MetodoPago.choices, default=MetodoPago.TARJETA)
    estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    monto = models.DecimalField(max_digits=12, decimal_places=2, help_text="Monto cobrado en COP")
    referencia = models.CharField(max_length=100, unique=True, help_text="Referencia única generada por Enviart")
    fecha_pago = models.DateTimeField(auto_now_add=True)
    detalles_adicionales = models.JSONField(null=True, blank=True, help_text="Campos extras de Wompi")

    class Meta:
        db_table = 'pedidos_pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Pago #{self.id} - Pedido #{self.pedido.id} - {self.estado}"

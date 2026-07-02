from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .choices import TipoReclamo, PrioridadReclamo
from .pedido import Pedido


class Reclamo(models.Model):
    """
    Sistema de reclamos y devoluciones.
    Similar al claims process de FedEx.
    """
    # ✅ Identificación única
    numero_reclamo = models.CharField(max_length=50, unique=True, db_index=True, editable=False)
    
    # ✅ Relación con pedido
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name='reclamos'
    )
    
    # ✅ Datos del reclamante
    reclamante = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.PROTECT,
        related_name='reclamos'
    )
    nombre_reclamante = models.CharField(max_length=100)
    email_reclamante = models.EmailField()
    telefono_reclamante = models.CharField(max_length=20)
    
    # ✅ Tipo y prioridad
    tipo = models.CharField(
        max_length=50,
        choices=TipoReclamo.choices
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadReclamo.choices,
        default=PrioridadReclamo.MEDIO
    )
    
    # ✅ Descripción
    descripcion = models.TextField(help_text='Descripción detallada del reclamo')
    descripcion_danos = models.TextField(null=True, blank=True, help_text='Si aplica por daño')
    
    # ✅ Valor reclamado
    valor_reclamado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_aprobado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # ✅ Estado del reclamo
    estado = models.CharField(
        max_length=30,
        choices=[
            ('RADICADO', 'Radicado'),
            ('EN_REVISION', 'En revisión'),
            ('EN_INVESTIGACION', 'En investigación'),
            ('APROBADO', 'Aprobado'),
            ('RECHAZADO', 'Rechazado'),
            ('PAGADO', 'Pagado'),
            ('CERRADO', 'Cerrado'),
        ],
        default='RADICADO'
    )
    
    # ✅ Fechas
    fecha_radicacion = models.DateTimeField(auto_now_add=True)
    fecha_limite_respuesta = models.DateTimeField(help_text='SLA de respuesta')
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # ✅ Asignación
    asignado_a = models.ForeignKey(
        'Autenticacion.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamos_asignados',
        help_text='Analista asignado'
    )
    
    # ✅ Evidencia
    documentos = models.JSONField(
        null=True,
        blank=True,
        help_text='URLs de documentos adjuntos (fotos, facturas, etc.)'
    )
    
    # ✅ Resolución
    resolucion = models.TextField(null=True, blank=True, help_text='Decisión final')
    motivo_rechazo = models.TextField(null=True, blank=True)
    
    # ✅ Pago (si aplica)
    numero_pago = models.CharField(max_length=50, null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_reclamo'
        verbose_name = 'Reclamo'
        verbose_name_plural = 'Reclamos'
        ordering = ['-fecha_radicacion']
        indexes = [
            models.Index(fields=['numero_reclamo']),
            models.Index(fields=['pedido', 'estado']),
            models.Index(fields=['estado', 'fecha_radicacion']),
            models.Index(fields=['reclamante', 'estado']),
        ]
    
    def __str__(self):
        return f'Reclamo {self.numero_reclamo} - {self.pedido.numero_pedido}'
    
    def save(self, *args, **kwargs):
        """Genera número de reclamo automático"""
        if not self.numero_reclamo:
            from django.utils import timezone
            year = timezone.now().year
            last_reclamo = Reclamo.objects.filter(
                numero_reclamo__startswith=f'REC-{year}-'
            ).order_by('-numero_reclamo').first()
            
            if last_reclamo:
                last_num = int(last_reclamo.numero_reclamo.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.numero_reclamo = f'REC-{year}-{new_num:06d}'
        
        # ✅ Calcular fecha límite (SLA según prioridad)
        if not self.fecha_limite_respuesta:
            from django.utils import timezone
            from datetime import timedelta
            
            sla_dias = {
                'BAJO': 10,
                'MEDIO': 5,
                'ALTO': 3,
                'CRITICO': 1,
            }
            dias = sla_dias.get(self.prioridad, 5)
            self.fecha_limite_respuesta = timezone.now() + timedelta(days=dias)
        
        super().save(*args, **kwargs)
    
    def aprobar(self, valor_aprobado, usuario_aprobador):
        """Aprueba el reclamo"""
        from django.utils import timezone
        self.estado = 'APROBADO'
        self.valor_aprobado = valor_aprobado
        self.fecha_resolucion = timezone.now()
        self.resolucion = f'Aprobado por {usuario_aprobador.email}'
        self.save()
    
    def rechazar(self, motivo, usuario_rechazador):
        """Rechaza el reclamo"""
        from django.utils import timezone
        self.estado = 'RECHAZADO'
        self.fecha_resolucion = timezone.now()
        self.motivo_rechazo = motivo
        self.resolucion = f'Rechazado por {usuario_rechazador.email}: {motivo}'
        self.save()
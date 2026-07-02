from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator


class TipoServicio(models.Model):
    """
    Tipos de servicio de envío con tarifas dinámicas.
    Similar a FedEx Standard, Express, Overnight, etc.
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, db_index=True)  # Ej: STD, EXP, ONT
    descripcion = models.TextField(blank=True)
    
    # ✅ Tiempos de entrega garantizados
    dias_entrega_min = models.PositiveIntegerField(default=1)
    dias_entrega_max = models.PositiveIntegerField(default=5)
    es_garantizado = models.BooleanField(default=False)
    
    # ✅ Tarifas base
    costo_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    costo_por_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    peso_max_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Peso máximo permitido para este servicio'
    )
    
    # ✅ Dimensiones máximas
    largo_max_cm = models.PositiveIntegerField(null=True, blank=True)
    ancho_max_cm = models.PositiveIntegerField(null=True, blank=True)
    alto_max_cm = models.PositiveIntegerField(null=True, blank=True)
    
    # ✅ Cobertura
    es_nacional = models.BooleanField(default=True)
    es_internacional = models.BooleanField(default=False)
    paises_disponibles = models.JSONField(
        null=True,
        blank=True,
        help_text='Lista de códigos de país si es internacional'
    )
    
    # ✅ Estado
    es_activo = models.BooleanField(default=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_tipo_servicio'
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicio'
        ordering = ['nombre']
    
    def __str__(self):
        return f'{self.nombre} ({self.codigo})'
    
    def calcular_tarifa(self, peso_kg, distancia_km=None, es_expresso=False):
        """
        Calcula la tarifa basada en peso y distancia.
        Puede extenderse con factores adicionales.
        """
        tarifa = self.costo_base
        
        if peso_kg > 1:
            tarifa += (peso_kg - 1) * self.costo_por_kg
        
        # ✅ Factor de distancia (opcional)
        if distancia_km and distancia_km > 100:
            tarifa += Decimal(distancia_km) * Decimal('0.01')
        
        # ✅ Factor express
        if es_expresso:
            tarifa *= Decimal('1.5')
        
        return tarifa.quantize(Decimal('0.01'))
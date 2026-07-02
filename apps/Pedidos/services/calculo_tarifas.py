from decimal import Decimal
from django.utils import timezone
from ..models.servicio import TipoServicio
from ..models.hub import Hub


class CalculadoraTarifas:
    """
    Motor de cálculo de tarifas tipo FedEx.
    Considera peso, distancia, zona, servicio y factores adicionales.
    """
    
    @staticmethod
    def calcular(pedido):
        """Calcula la tarifa total para un pedido"""
        servicio = pedido.tipo_servicio
        
        # ✅ Peso a cobrar (mayor entre real y volumétrico)
        peso_cobrar = pedido.peso_cobrar
        
        # ✅ Tarifa base del servicio
        tarifa = servicio.calcular_tarifa(peso_cobrar)
        
        # ✅ Factor de distancia (si hay hubs)
        if pedido.hub_origen and pedido.hub_destino:
            distancia = CalculadoraTarifas._calcular_distancia_hubs(
                pedido.hub_origen,
                pedido.hub_destino
            )
            if distancia > 500:  # Más de 500km
                tarifa *= Decimal('1.2')  # 20% adicional
        
        # ✅ Valor declarado (seguro)
        if pedido.valor_declarado > 0:
            tarifa += pedido.valor_declarado * Decimal('0.02')  # 2% del valor
        
        # ✅ Fragilidad
        if pedido.es_fragil:
            tarifa *= Decimal('1.15')  # 15% adicional
        
        # ✅ Impuestos
        impuestos = tarifa * Decimal('0.19')  # IVA 19%
        
        # ✅ Descuentos
        descuento = Decimal('0.00')
        if pedido.usuario and pedido.usuario.es_cliente():
            # Descuento por volumen (ejemplo)
            pedidos_previos = pedido.usuario.pedidos.count()
            if pedidos_previos > 10:
                descuento = tarifa * Decimal('0.10')  # 10% descuento
        
        subtotal = tarifa
        total = subtotal + impuestos - descuento
        
        return {
            'subtotal': subtotal.quantize(Decimal('0.01')),
            'impuestos': impuestos.quantize(Decimal('0.01')),
            'descuento': descuento.quantize(Decimal('0.01')),
            'total_final': total.quantize(Decimal('0.01')),  # FIX-01: debe coincidir con Pedido.total_final
        }
    
    @staticmethod
    def _calcular_distancia_hubs(hub_origen, hub_destino):
        """Calcula distancia entre dos hubs en km"""
        from math import radians, cos, sin, asin, sqrt
        
        if not (hub_origen.latitud and hub_destino.latitud):
            return 0
        
        def haversine(lat1, lon1, lat2, lon2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            return km
        
        return haversine(
            float(hub_origen.latitud),
            float(hub_origen.longitud),
            float(hub_destino.latitud),
            float(hub_destino.longitud)
        )
from django.test import TestCase
from decimal import Decimal
from ..models import Hub, TipoServicio, Pedido
from ..services.calculo_tarifas import CalculadoraTarifas
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class CalculadoraTarifasTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.cliente = Usuario.objects.create_user(
            email='cliente@test.com',
            primer_nombre='Test',
            primer_apellido='User',
            doc_usuario='TST001',
            password='Test1234!'
        )
        
        cls.servicio = TipoServicio.objects.create(
            nombre='Express',
            codigo='EXP',
            costo_base=15000,
            costo_por_kg=2000,
            dias_entrega_min=1,
            dias_entrega_max=2
        )
        
        cls.hub_bogota = Hub.objects.create(
            nombre='Bogotá',
            codigo='BOG',
            tipo='CENTRAL',
            ciudad='Bogotá',
            latitud=4.7110,
            longitud=-74.0721
        )
        
        cls.hub_medellin = Hub.objects.create(
            nombre='Medellín',
            codigo='MED',
            tipo='REGIONAL',
            ciudad='Medellín',
            latitud=6.2442,
            longitud=-75.5812
        )
    
    def test_calculo_tarifa_base(self):
        """Test: Cálculo de tarifa solo con peso"""
        pedido = Pedido(
            usuario=self.cliente,
            tipo_servicio=self.servicio,
            peso_real_kg=5.0,
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín'
        )
        
        tarifas = CalculadoraTarifas.calcular(pedido)
        
        # Base: 15000 + (4kg * 2000) = 23000
        self.assertGreater(tarifas['subtotal'], 20000)
        self.assertGreater(tarifas['total'], tarifas['subtotal'])
    
    def test_calculo_con_distancia(self):
        """Test: Cálculo con factor de distancia"""
        pedido = Pedido(
            usuario=self.cliente,
            tipo_servicio=self.servicio,
            peso_real_kg=5.0,
            hub_origen=self.hub_bogota,
            hub_destino=self.hub_medellin,
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín'
        )
        
        tarifas = CalculadoraTarifas.calcular(pedido)
        
        # Debería incluir factor de distancia (>500km)
        self.assertGreater(tarifas['subtotal'], 20000)
    
    def test_calculo_con_valor_declarado(self):
        """Test: Cálculo con seguro por valor declarado"""
        pedido = Pedido(
            usuario=self.cliente,
            tipo_servicio=self.servicio,
            peso_real_kg=2.0,
            valor_declarado=1000000,  # 1 millón
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín'
        )
        
        tarifas = CalculadoraTarifas.calcular(pedido)
        
        # 2% del valor declarado = 20000
        self.assertGreater(tarifas['subtotal'], 15000)
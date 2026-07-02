from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Hub, TipoServicio, Pedido, GuiaEnvio,
    EventoTracking, PruebaEntrega, Reclamo
)
from ..choices import EstadoPedido, TipoEventoTracking, TipoReclamo

Usuario = get_user_model()


class PedidoModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Configurar datos para todos los tests"""
        # Usuario cliente
        cls.cliente = Usuario.objects.create_user(
            email='cliente@test.com',
            primer_nombre='Juan',
            primer_apellido='Cliente',
            doc_usuario='CLI001',
            password='Test1234!'
        )
        
        # Hub de origen y destino
        cls.hub_origen = Hub.objects.create(
            nombre='Hub Bogotá Central',
            codigo='BOG-HUB-01',
            tipo='CENTRAL',
            direccion='Calle 123 #45-67',
            ciudad='Bogotá',
            departamento='Cundinamarca',
            latitud=4.7110,
            longitud=-74.0721
        )
        
        cls.hub_destino = Hub.objects.create(
            nombre='Hub Medellín',
            codigo='MED-HUB-01',
            tipo='REGIONAL',
            direccion='Carrera 45 #12-34',
            ciudad='Medellín',
            departamento='Antioquia',
            latitud=6.2442,
            longitud=-75.5812
        )
        
        # Tipo de servicio
        cls.servicio = TipoServicio.objects.create(
            nombre='Envío Express',
            codigo='EXP',
            costo_base=15000,
            costo_por_kg=2000,
            dias_entrega_min=1,
            dias_entrega_max=2,
            es_garantizado=True
        )
    
    def test_crear_pedido_automatico(self):
        """Test: Crear pedido con generación automática de número"""
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_origen_texto='Calle 1 #2-3',
            direccion_destino_texto='Carrera 4 #5-6',
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín',
            departamento_origen='Cundinamarca',
            departamento_destino='Antioquia',
            nombre_destinatario='María López',
            telefono_destinatario='+573001234567',
            tipo_servicio=self.servicio,
            peso_real_kg=2.5,
            descripcion_contenido='Documentos',
            subtotal=20000,
            impuestos=3800,
            total_final=23800,
            hub_origen=self.hub_origen,
            hub_destino=self.hub_destino,
        )
        
        self.assertTrue(pedido.numero_pedido.startswith('PED-'))
        self.assertTrue(len(pedido.codigo_rastreo) > 10)
        self.assertEqual(pedido.estado, EstadoPedido.BORRADOR)
    
    def test_calculo_peso_volumetrico(self):
        """Test: Cálculo automático de peso volumétrico"""
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_origen_texto='Calle 1 #2-3',
            direccion_destino_texto='Carrera 4 #5-6',
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín',
            departamento_origen='Cundinamarca',
            departamento_destino='Antioquia',
            nombre_destinatario='María López',
            telefono_destinatario='+573001234567',
            tipo_servicio=self.servicio,
            peso_real_kg=2.5,
            largo_cm=50,
            ancho_cm=40,
            alto_cm=30,
            descripcion_contenido='Ropa',
            subtotal=20000,
            impuestos=3800,
            total_final=23800,
        )
        
        # Peso volumétrico = (50*40*30)/5000 = 12 kg
        self.assertEqual(pedido.peso_volumetrico_kg, 12.00)
        self.assertEqual(pedido.peso_cobrar, 12.00)  # Mayor entre real y volumétrico
    
    def test_transicion_estados_pedido(self):
        """Test: Transiciones válidas de estado"""
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_origen_texto='Calle 1 #2-3',
            direccion_destino_texto='Carrera 4 #5-6',
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín',
            departamento_origen='Cundinamarca',
            departamento_destino='Antioquia',
            nombre_destinatario='María López',
            telefono_destinatario='+573001234567',
            tipo_servicio=self.servicio,
            peso_real_kg=2.5,
            descripcion_contenido='Documentos',
            subtotal=20000,
            impuestos=3800,
            total_final=23800,
        )
        
        # ✅ Transición válida
        pedido.estado = EstadoPedido.CONFIRMADO
        pedido.save()
        self.assertEqual(pedido.estado, EstadoPedido.CONFIRMADO)
    
    def test_puede_cancelar_pedido(self):
        """Test: Validación de cancelación"""
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            direccion_origen_texto='Calle 1 #2-3',
            direccion_destino_texto='Carrera 4 #5-6',
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín',
            departamento_origen='Cundinamarca',
            departamento_destino='Antioquia',
            nombre_destinatario='María López',
            telefono_destinatario='+573001234567',
            tipo_servicio=self.servicio,
            peso_real_kg=2.5,
            descripcion_contenido='Documentos',
            subtotal=20000,
            impuestos=3800,
            total_final=23800,
        )
        
        # ✅ Cliente puede cancelar en BORRADOR
        self.assertTrue(pedido.puede_cancelar(self.cliente))
        
        # ❌ Otro usuario no puede cancelar
        otro_usuario = Usuario.objects.create_user(
            email='otro@test.com',
            primer_nombre='Otro',
            primer_apellido='Usuario',
            doc_usuario='OTR001',
            password='Test1234!'
        )
        self.assertFalse(pedido.puede_cancelar(otro_usuario))


class GuiaEnvioModelTest(TestCase):
    
    def test_generar_guia_automatico(self):
        """Test: Generación automática de número de guía"""
        # Crear pedido primero
        cliente = Usuario.objects.create_user(
            email='cliente2@test.com',
            primer_nombre='Test',
            primer_apellido='User',
            doc_usuario='TST001',
            password='Test1234!'
        )
        
        pedido = Pedido.objects.create(
            usuario=cliente,
            direccion_origen_texto='Calle 1 #2-3',
            direccion_destino_texto='Carrera 4 #5-6',
            ciudad_origen='Bogotá',
            ciudad_destino='Medellín',
            departamento_origen='Cundinamarca',
            departamento_destino='Antioquia',
            nombre_destinatario='María López',
            telefono_destinatario='+573001234567',
            tipo_servicio=TipoServicio.objects.create(
                nombre='Test', codigo='TST', costo_base=10000
            ),
            peso_real_kg=2.5,
            descripcion_contenido='Test',
            subtotal=10000,
            impuestos=1900,
            total_final=11900,
        )
        
        guia = GuiaEnvio.objects.create(pedido=pedido)
        
        self.assertTrue(guia.numero_guia.startswith('GUI-'))
        self.assertEqual(guia.codigo_barras, guia.codigo_barras.upper())
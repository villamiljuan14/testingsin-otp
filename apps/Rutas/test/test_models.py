from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Ruta, ParadaRuta, EstadoRuta
from apps.Pedidos.models import Hub

Usuario = get_user_model()


class RutaModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Configurar datos para todos los tests"""
        cls.hub = Hub.objects.create(
            nombre='Hub Central',
            codigo='HUB-001',
            tipo='CENTRAL',
            ciudad='Bogotá'
        )
        
        cls.usuario = Usuario.objects.create_user(
            email='planificador@test.com',
            primer_nombre='Planificador',
            primer_apellido='Test',
            doc_usuario='PLAN001',
            password='Test1234!'
        )
    
    def test_crear_ruta_automatico(self):
        """Test: Crear ruta con generación automática de código"""
        ruta = Ruta.objects.create(
            nombre='Ruta Test 1',
            hub_origen=self.hub,
            fecha_programada='2025-01-15',
            creado_por=self.usuario
        )
        
        self.assertTrue(ruta.codigo_ruta.startswith('RUTA-'))
        self.assertEqual(ruta.estado, EstadoRuta.BORRADOR)
    
    def test_puede_iniciar_ruta(self):
        """Test: Verificar si la ruta puede ser iniciada"""
        ruta = Ruta.objects.create(
            nombre='Ruta Test 2',
            hub_origen=self.hub,
            fecha_programada='2025-01-15',
            estado=EstadoRuta.ASIGNADA,
            creado_por=self.usuario
        )
        
        # ✅ No puede iniciar sin paradas
        self.assertFalse(ruta.puede_iniciar())
        
        # ✅ Agregar parada
        ParadaRuta.objects.create(
            ruta=ruta,
            orden_parada=1,
            direccion_completa='Calle 1 #2-3'
        )
        
        # ✅ Sigue sin poder iniciar (sin vehículo asignado)
        self.assertFalse(ruta.puede_iniciar())
    
    def test_porcentaje_completado(self):
        """Test: Calcular porcentaje de completitud"""
        ruta = Ruta.objects.create(
            nombre='Ruta Test 3',
            hub_origen=self.hub,
            fecha_programada='2025-01-15',
            creado_por=self.usuario
        )
        
        # ✅ Crear 4 paradas
        for i in range(1, 5):
            ParadaRuta.objects.create(
                ruta=ruta,
                orden_parada=i,
                direccion_completa=f'Dirección {i}',
                estado='PENDIENTE' if i > 2 else 'COMPLETADA'
            )
        
        # ✅ 2 de 4 completadas = 50%
        self.assertEqual(ruta.porcentaje_completado, 50.0)
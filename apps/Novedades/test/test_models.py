from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Novedad, CategoriaNovedad, EstadoNovedad, SeveridadNovedad

Usuario = get_user_model()


class NovedadModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            email='test@test.com',
            primer_nombre='Test',
            primer_apellido='User',
            doc_usuario='TST001',
            password='Test1234!'
        )
        
        cls.categoria = CategoriaNovedad.objects.create(
            nombre='Entrega',
            codigo='ENT',
            sla_horas_respuesta=24,
            sla_horas_resolucion=72
        )
    
    def test_crear_novedad_automatico(self):
        """Test: Crear novedad con código automático"""
        novedad = Novedad.objects.create(
            titulo='Novedad Test',
            descripcion='Descripción de prueba',
            tipo='INCIDENCIA',
            registrado_por=self.usuario
        )
        
        self.assertTrue(novedad.codigo_novedad.startswith('NOV-'))
        self.assertEqual(novedad.estado, EstadoNovedad.REGISTRADA)
    
    def test_sla_vencido(self):
        """Test: Verificar SLA vencido"""
        from django.utils import timezone
        from datetime import timedelta
        
        novedad = Novedad.objects.create(
            titulo='Novedad SLA',
            descripcion='Test SLA',
            tipo='INCIDENCIA',
            registrado_por=self.usuario,
            fecha_limite_resolucion=timezone.now() - timedelta(hours=1)
        )
        
        self.assertTrue(novedad.sla_vencido)
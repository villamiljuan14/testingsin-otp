from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models.rol import Rol
from ..models.choices import TipoRol, TipoDocumento

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    
    def setUp(self):
        self.rol_cliente = Rol.objects.create(
            nombre_rol='Cliente',
            tipo_rol=TipoRol.CLIENTE
        )
    
    def test_crear_usuario(self):
        user = Usuario.objects.create_user(
            email='test@example.com',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            doc_usuario='123456789',
            password='password123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_crear_superuser(self):
        admin = Usuario.objects.create_superuser(
            email='admin@enviart.com',
            primer_nombre='Manuel',
            primer_apellido='Vargas',
            doc_usuario='100000000',
            password='admin123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_nombre_completo(self):
        user = Usuario.objects.create_user(
            email='test2@example.com',
            primer_nombre='María',
            segundo_nombre='José',
            primer_apellido='García',
            segundo_apellido='López',
            doc_usuario='987654321',
            password='password123'
        )
        self.assertEqual(user.nombre_completo, 'María José García López')
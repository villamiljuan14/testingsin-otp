from django.test import TestCase, Client
from django.urls import reverse
from apps.Autenticacion.models import Usuario, Rol
from apps.Pedido.models import Pedido, EstadoPedido, TipoServicio, Direccion
from django.utils import timezone
from decimal import Decimal

class PedidoExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup Rol and User
        self.rol = Rol.objects.create(nombre_rol='Admin', tipo_rol='ADMIN')
        self.user = Usuario.objects.create_user(
            email='admin@enviart.com',
            password='password123',
            primer_nombre='Admin',
            primer_apellido='User',
            doc_usuario='12345678',
            rol=self.rol
        )
        self.client.login(email='admin@enviart.com', password='password123')
        
        # Setup Pedido dependencies
        self.estado_pend = EstadoPedido.objects.create(nombre='Pendiente', orden=1)
        self.estado_ent = EstadoPedido.objects.create(nombre='Entregado', orden=2)
        self.tipo_serv = TipoServicio.objects.create(nombre='Estándar', costo_base=Decimal('10.00'))
        self.dir_orig = Direccion.objects.create(calle='Calle 1', numero='123', ciudad='Bogotá', codigo_postal='110111')
        self.dir_dest = Direccion.objects.create(calle='Calle 2', numero='456', ciudad='Medellín', codigo_postal='050001')
        
        # Create Pedidos
        self.p1 = Pedido.objects.create(
            usuario=self.user,
            direccion_origen=self.dir_orig,
            direccion_destino=self.dir_dest,
            tipo_servicio=self.tipo_serv,
            total_final=Decimal('100.00'),
            fecha_pedido=timezone.now(),
            estado=self.estado_pend
        )
        
        self.p2 = Pedido.objects.create(
            usuario=self.user,
            direccion_origen=self.dir_orig,
            direccion_destino=self.dir_dest,
            tipo_servicio=self.tipo_serv,
            total_final=Decimal('200.00'),
            fecha_pedido=timezone.now(),
            estado=self.estado_ent
        )

    def test_pedidos_list_no_filter(self):
        response = self.client.get(reverse('pedidos_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pedidos']), 2)

    def test_pedidos_list_filter_status(self):
        response = self.client.get(reverse('pedidos_list'), {'estado': self.estado_ent.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pedidos']), 1)
        self.assertEqual(response.context['pedidos'][0].id, self.p2.id)

    def test_export_pdf_status_code(self):
        response = self.client.get(reverse('export_pedidos_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.has_header('Content-Disposition'))

    def test_pedido_create_view(self):
        response = self.client.get(reverse('pedido_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pedido_form.html')

    def test_pedido_update_view(self):
        response = self.client.get(reverse('pedido_update', args=[self.p1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pedido_form.html')

    def test_pedido_delete_view(self):
        response = self.client.get(reverse('pedido_delete', args=[self.p1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/pedido_confirm_delete.html')

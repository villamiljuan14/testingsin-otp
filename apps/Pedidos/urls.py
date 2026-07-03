# apps/Pedidos/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views.dashboard import (
    dashboard_pedidos_list, dashboard_guias_list, dashboard_tracking_list,
    dashboard_servicios_list, dashboard_hubs_list, dashboard_reclamos_list,
    tracking_create, tracking_update, tracking_delete,
    guia_create_dashboard_view, guia_update_view, guia_delete_view,
    hub_create_view, hub_update_view, hub_delete_view,
    servicio_create_view, servicio_update_view, servicio_delete_view,
    reclamo_create_view, reclamo_update_view, reclamo_delete_view,
    export_pedidos_view, export_guias_view, export_hubs_view,
    export_servicios_view, export_reclamos_view, export_tracking_view
)
from .views.pedido_create import pedido_create_view, pedido_detail_view, pedido_update_view, pedido_delete_view
from .views.pago_views import checkout_pago_view, wompi_webhook_view
from .views.mock_wompi import mock_wompi_checkout, mock_wompi_widget_script

router = DefaultRouter()
router.register(r'pedidos', views.PedidoViewSet, basename='pedido')
router.register(r'guias', views.GuiaEnvioViewSet, basename='guia')
router.register(r'tracking', views.TrackingViewSet, basename='tracking')
router.register(r'reclamos', views.ReclamoViewSet, basename='reclamo')
router.register(r'hubs', views.HubViewSet, basename='hub')
router.register(r'servicios', views.TipoServicioViewSet, basename='servicio')

urlpatterns = [
    # ==================== API REST ENDPOINTS ====================
    
    path('api/', include(router.urls)),
    
    path('api/pedidos/<int:pk>/generar-guia/', views.GenerarGuiaView.as_view(), name='generar-guia'),
    path('api/pedidos/<int:pk>/registrar-entrega/', views.RegistrarEntregaView.as_view(), name='registrar-entrega'),
    
    # Tracking público (sin autenticación)
    path('public/tracking/<str:codigo_rastreo>/', views.TrackingPublicoView.as_view(), name='tracking-publico'),
    
    # ==================== DASHBOARD ENDPOINTS ====================
    path('dashboard/pedidos/', dashboard_pedidos_list, name='dashboard_pedidos'),
    path('dashboard/pedidos/nuevo/', pedido_create_view, name='pedido_create'),
    path('dashboard/pedidos/<int:pedido_id>/', pedido_detail_view, name='pedido_detail'),
    path('dashboard/pedidos/<int:pedido_id>/editar/', pedido_update_view, name='pedido_update'),
    path('dashboard/pedidos/<int:pedido_id>/eliminar/', pedido_delete_view, name='pedido_delete'),
    path('dashboard/guias/', dashboard_guias_list, name='dashboard_guias'),
    path('dashboard/guias/<int:pk>/editar/', guia_update_view, name='guia_update'),
    path('dashboard/guias/<int:pk>/eliminar/', guia_delete_view, name='guia_delete'),
    path('dashboard/pedidos/<int:pedido_id>/generar-guia-dashboard/', guia_create_dashboard_view, name='guia_create_dashboard'),
    path('dashboard/tracking/', dashboard_tracking_list, name='dashboard_tracking'),
    path('dashboard/tracking/nuevo/', tracking_create, name='tracking_create'),
    path('dashboard/tracking/<int:pk>/editar/', tracking_update, name='tracking_update'),
    path('dashboard/tracking/<int:pk>/eliminar/', tracking_delete, name='tracking_delete'),
    path('dashboard/servicios/', dashboard_servicios_list, name='dashboard_servicios'),
    path('dashboard/servicios/nuevo/', servicio_create_view, name='servicio_create'),
    path('dashboard/servicios/<int:pk>/editar/', servicio_update_view, name='servicio_update'),
    path('dashboard/servicios/<int:pk>/eliminar/', servicio_delete_view, name='servicio_delete'),
    path('dashboard/hubs/', dashboard_hubs_list, name='dashboard_hubs'),
    path('dashboard/hubs/nuevo/', hub_create_view, name='hub_create'),
    path('dashboard/hubs/<int:pk>/editar/', hub_update_view, name='hub_update'),
    path('dashboard/hubs/<int:pk>/eliminar/', hub_delete_view, name='hub_delete'),
    path('dashboard/reclamos/', dashboard_reclamos_list, name='dashboard_reclamos'),
    path('dashboard/reclamos/nuevo/', reclamo_create_view, name='reclamo_create'),
    path('dashboard/reclamos/<int:pk>/editar/', reclamo_update_view, name='reclamo_update'),
    path('dashboard/reclamos/<int:pk>/eliminar/', reclamo_delete_view, name='reclamo_delete'),
    path('dashboard/pedidos/export/<str:file_format>/', export_pedidos_view, name='export_pedidos'),
    path('dashboard/guias/export/<str:file_format>/', export_guias_view, name='export_guias'),
    path('dashboard/hubs/export/<str:file_format>/', export_hubs_view, name='export_hubs'),
    path('dashboard/servicios/export/<str:file_format>/', export_servicios_view, name='export_servicios'),
    path('dashboard/reclamos/export/<str:file_format>/', export_reclamos_view, name='export_reclamos'),
    path('dashboard/tracking/export/<str:file_format>/', export_tracking_view, name='export_tracking'),
    path('dashboard/pedidos/<int:pedido_id>/checkout-pago/', checkout_pago_view, name='checkout_pago'),
    
    # ==================== MOCK WOMPI (Testing sin conexión externa) ====================
    path('mock/wompi/checkout/', mock_wompi_checkout, name='mock_wompi_checkout'),
    path('mock/wompi/widget.js', mock_wompi_widget_script, name='mock_wompi_widget'),
    
    # ==================== WOMPI WEBHOOKS ====================
    path('payments/wompi-webhook/', wompi_webhook_view, name='wompi_webhook'),
]
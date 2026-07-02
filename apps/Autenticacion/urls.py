from django.urls import path
from .views.auth import LoginView, RegistroView, LogoutView
from .views.usuario import PerfilView
from .views.classic import (
    login_view, register_view, logout_view,
    usuario_list_view, usuario_create_view, usuario_update_view, usuario_delete_view, export_usuarios_view
)
from apps.core.views_dashboard import dashboard_principal_view
from apps.core import views as core_views

urlpatterns = [
    # API REST endpoints (Option A)
    path('api/auth/login/', LoginView.as_view(), name='api_login'),
    path('api/auth/register/', RegistroView.as_view(), name='api_register'),
    path('api/auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/auth/perfil/', PerfilView.as_view(), name='api_perfil'),

    # UI endpoints (templates)
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # Dashboard principal - redirige a vista con KPIs
    path('dashboard/', dashboard_principal_view, name='dashboard_index'),
    
    # Dashboard de usuarios movido a ruta específica y sin conflicto de nombre
    # path('dashboard/', usuario_list_view, name='dashboard_usuarios'),  # no utilizar
    path('dashboard/inicio/', usuario_list_view, name='dashboard_usuarios_inicio'),
    
    # Dashboards por rol
    path('dashboard/cliente/', core_views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/mensajero/', core_views.dashboard_mensajero, name='dashboard_mensajero'),
    path('dashboard/proveedor/', core_views.dashboard_proveedor, name='dashboard_proveedor'),

    # Dashboard usuarios
    path('dashboard/usuarios/', usuario_list_view, name='usuarios_list'),
    path('dashboard/usuarios/nuevo/', usuario_create_view, name='usuario_create'),
    path('dashboard/usuarios/<int:pk>/editar/', usuario_update_view, name='usuario_update'),
    path('dashboard/usuarios/<int:pk>/eliminar/', usuario_delete_view, name='usuario_delete'),
    path('dashboard/usuarios/export/<str:file_format>/', export_usuarios_view, name='export_usuarios'),
]
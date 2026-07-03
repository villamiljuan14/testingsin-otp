"""
URL configuration for Enviart project.
# Force reload for templates
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse


from apps.core.views_rastreo import rastreo_publico_view, contacto_view

def dummy_view(request):
    return HttpResponse("Página en construcción")

urlpatterns = [
    # Health check para Railway (GET → 200 OK)
    path('health/', lambda request: HttpResponse('OK'), name='health'),

    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('servicios/', TemplateView.as_view(template_name='servicios.html'), name='servicios'),
    path('forgot-password/', TemplateView.as_view(template_name='forgot_password.html'), name='forgot_password'),
    path('contacto/', contacto_view, name='contacto'),
    path('rastrear/', rastreo_publico_view, name='rastrear'),

    # ✅ URLs ordenadas por prioridad y especificidad
    path('', include('apps.Ubicaciones.urls')),  # ✅ API de ubicaciones (sin dependencias)
    path('', include('apps.Pedidos.urls')),  # ✅ Módulo de pedidos moderno
    path('', include('apps.Autenticacion.urls')),  # ✅ Autenticación y usuarios
    
    # ❌ Apps con problemas temporales
    path('', include('apps.Rutas.urls')),  # Gestión de rutas habilitada
    # path('', include('apps.core.urls')),  # Dashboard - temporalmente desactivado
    # path('', include('apps.Pedido.urls')),  # Legacy - temporalmente desactivado
    # path('', include('apps.Novedades.urls')),  # Desactivado por circular import
]

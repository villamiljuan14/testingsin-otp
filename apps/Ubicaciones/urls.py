from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ✅ Router para API REST
router = DefaultRouter()
router.register(r'paises', views.PaisViewSet, basename='pais')
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'ciudades', views.CiudadViewSet, basename='ciudad')
router.register(r'hubs', views.HubViewSet, basename='hub')

urlpatterns = [
    # API REST endpoints
    path('api/', include(router.urls)),
    
    # Endpoints especiales
    path('api/ubicaciones/cascada/', views.ubicaciones_en_cascada, name='ubicaciones_cascada'),
    path('api/ubicaciones/buscar/', views.buscar_ciudades, name='buscar_ciudades'),
]
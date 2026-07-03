from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/rutas', views.RutaViewSet)

urlpatterns = [
    # API
    path('', include(router.urls)),

    # Vehículos (Dashboard)
    path('dashboard/vehiculos/', views.VehiculoListView.as_view(), name='vehiculos_list'),
    path('dashboard/vehiculos/nuevo/', views.VehiculoCreateView.as_view(), name='vehiculo_create'),
    path('dashboard/vehiculos/<int:pk>/editar/', views.VehiculoUpdateView.as_view(), name='vehiculo_update'),
    path('dashboard/vehiculos/<int:pk>/eliminar/', views.VehiculoDeleteView.as_view(), name='vehiculo_delete'),
    path('dashboard/vehiculos/export/<str:file_format>/', views.ExportVehiculosView.as_view(), name='export_vehiculos'),

    # Rutas (Dashboard)
    path('dashboard/rutas/', views.RutaListView.as_view(), name='rutas_list'),
    path('dashboard/rutas/nuevo/', views.RutaCreateView.as_view(), name='ruta_create'),
    path('dashboard/rutas/<int:pk>/editar/', views.RutaUpdateView.as_view(), name='ruta_update'),
    path('dashboard/rutas/<int:pk>/eliminar/', views.RutaDeleteView.as_view(), name='ruta_delete'),
    path('dashboard/rutas/export/<str:file_format>/', views.ExportRutasView.as_view(), name='export_rutas'),
]

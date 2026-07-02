from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/mensajero/', views.dashboard_mensajero, name='dashboard_mensajero'),
    path('dashboard/proveedor/', views.dashboard_proveedor, name='dashboard_proveedor'),
]

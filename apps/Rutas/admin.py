from django.contrib import admin
# from .models import Vehiculo, Ruta  # Temporarily disabled due to import issues

# @admin.register(Vehiculo)
# class VehiculoAdmin(admin.ModelAdmin):
#     list_display = ('placa', 'marca_vehiculo', 'modelo', 'tipo_vehiculo', 'capacidad_peso', 'estado_vehiculo')
#     list_filter = ('estado_vehiculo', 'tipo_vehiculo', 'marca_vehiculo')
#     search_fields = ('placa', 'marca_vehiculo', 'modelo')

# @admin.register(Ruta)
# class RutaAdmin(admin.ModelAdmin):
#     list_display = ('id', 'nombre_ruta', 'vehiculo', 'conductor', 'status_ruta', 'fecha_inicio')
#     list_filter = ('status_ruta', 'fecha_inicio')
#     search_fields = ('nombre_ruta',)
#     raw_id_fields = ('conductor',)

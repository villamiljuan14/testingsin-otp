from django.contrib import admin
from .models import Novedad, CategoriaNovedad, EvidenciaNovedad, AccionCorrectiva, SeguimientoNovedad, SLANovedad, MetricaNovedad


@admin.register(Novedad)
class NovedadAdmin(admin.ModelAdmin):
    list_display = ['codigo_novedad', 'titulo', 'tipo', 'severidad', 'estado', 'asignado_a', 'fecha_registro']
    list_filter = ['estado', 'severidad', 'tipo', 'fecha_registro']
    search_fields = ['codigo_novedad', 'titulo', 'descripcion']
    readonly_fields = ['codigo_novedad', 'fecha_registro', 'creado_en', 'actualizado_en']


@admin.register(CategoriaNovedad)
class CategoriaNovedadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'severidad_default', 'sla_horas_respuesta', 'es_activa']
    list_filter = ['es_activa', 'categoria_padre']
    search_fields = ['nombre', 'codigo']


@admin.register(EvidenciaNovedad)
class EvidenciaNovedadAdmin(admin.ModelAdmin):
    list_display = ['novedad', 'tipo', 'subido_por', 'creado_en']
    list_filter = ['tipo', 'creado_en']


@admin.register(AccionCorrectiva)
class AccionCorrectivaAdmin(admin.ModelAdmin):
    list_display = ['novedad', 'tipo', 'responsable', 'estado', 'fecha_limite']
    list_filter = ['estado', 'tipo', 'fecha_limite']


@admin.register(SeguimientoNovedad)
class SeguimientoNovedadAdmin(admin.ModelAdmin):
    list_display = ['novedad', 'campo_cambiado', 'usuario', 'fecha_cambio']
    list_filter = ['campo_cambiado', 'fecha_cambio']


@admin.register(SLANovedad)
class SLANovedadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tiempo_respuesta_horas', 'tiempo_resolucion_horas', 'es_activo']
    list_filter = ['es_activo', 'categoria']


@admin.register(MetricaNovedad)
class MetricaNovedadAdmin(admin.ModelAdmin):
    list_display = ['fecha_inicio', 'fecha_fin', 'total_novedades', 'porcentaje_cumplimiento_sla']
    list_filter = ['fecha_inicio']
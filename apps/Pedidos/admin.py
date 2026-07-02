from django.contrib import admin
from .models import (
    Hub, TipoServicio, Pedido, GuiaEnvio,
    EventoTracking, PruebaEntrega, Reclamo, NotificacionEnvio
)


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'ciudad', 'es_activo']
    list_filter = ['tipo', 'es_activo', 'departamento']
    search_fields = ['codigo', 'nombre', 'direccion']
    readonly_fields = ['creado_en', 'actualizado_en']


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'costo_base', 'dias_entrega_min', 'dias_entrega_max', 'es_activo']
    list_filter = ['es_activo', 'es_nacional', 'es_internacional']
    search_fields = ['nombre', 'codigo']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'codigo_rastreo', 'usuario', 'estado',
        'total_final', 'fecha_pedido', 'mensajero'
    ]
    list_filter = ['estado', 'tipo_servicio', 'fecha_pedido', 'hub_origen', 'hub_destino']
    search_fields = ['numero_pedido', 'codigo_rastreo', 'usuario__email', 'nombre_destinatario']
    readonly_fields = [
        'numero_pedido', 'codigo_rastreo', 'peso_volumetrico_kg',
        'direccion_origen_texto', 'direccion_destino_texto',
        'fecha_pedido', 'creado_en', 'actualizado_en'
    ]
    fieldsets = (
        ('Identificación', {
            'fields': ('numero_pedido', 'codigo_rastreo', 'usuario', 'estado')
        }),
        ('Direcciones', {
            'fields': (
                'direccion_origen_calle', 'direccion_origen_numero',
                'direccion_origen_barrio', 'direccion_origen_referencia',
                'direccion_destino_calle', 'direccion_destino_numero',
                'direccion_destino_barrio', 'direccion_destino_referencia',
                'ciudad_origen', 'ciudad_destino', 'departamento_origen',
                'departamento_destino', 'pais_origen', 'pais_destino',
                'direccion_origen_texto', 'direccion_destino_texto',
            )
        }),
        ('Destinatario', {
            'fields': ('nombre_destinatario', 'telefono_destinatario', 'email_destinatario')
        }),
        ('Servicio', {
            'fields': ('tipo_servicio', 'hub_origen', 'hub_destino', 'mensajero')
        }),
        ('Dimensiones y Peso', {
            'fields': (
                'peso_real_kg', 'peso_volumetrico_kg',
                'largo_cm', 'ancho_cm', 'alto_cm'
            )
        }),
        ('Contenido', {
            'fields': ('descripcion_contenido', 'valor_declarado', 'es_fragil', 'requiere_firma')
        }),
        ('Costos', {
            'fields': ('subtotal', 'descuento', 'impuestos', 'total_final')
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_estimada_entrega', 'fecha_entrega_real')
        }),
        ('Notas', {
            'fields': ('instrucciones_entrega', 'notas_internas')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GuiaEnvio)
class GuiaEnvioAdmin(admin.ModelAdmin):
    list_display = ['numero_guia', 'pedido', 'estado', 'fecha_generacion', 'generada_por']
    list_filter = ['estado', 'fecha_generacion']
    search_fields = ['numero_guia', 'codigo_barras', 'pedido__numero_pedido']
    readonly_fields = ['numero_guia', 'fecha_generacion', 'creado_en', 'actualizado_en']


@admin.register(EventoTracking)
class EventoTrackingAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'tipo_evento', 'ubicacion_texto', 'fecha_registro', 'registrado_por']
    list_filter = ['tipo_evento', 'fecha_registro', 'hub']
    search_fields = ['pedido__numero_pedido', 'ubicacion_texto']
    readonly_fields = ['fecha_registro']


@admin.register(PruebaEntrega)
class PruebaEntregaAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'nombre_recibidor', 'mensajero', 'fecha_entrega', 'es_validada']
    list_filter = ['es_validada', 'fecha_entrega', 'relacion_destinatario']
    search_fields = ['pedido__numero_pedido', 'nombre_recibidor', 'mensajero__email']
    readonly_fields = ['fecha_entrega', 'creado_en', 'actualizado_en']


@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ['numero_reclamo', 'pedido', 'tipo', 'prioridad', 'estado', 'valor_reclamado']
    list_filter = ['tipo', 'prioridad', 'estado', 'fecha_radicacion']
    search_fields = ['numero_reclamo', 'pedido__numero_pedido', 'reclamante__email']
    readonly_fields = ['numero_reclamo', 'fecha_radicacion', 'fecha_limite_respuesta']


@admin.register(NotificacionEnvio)
class NotificacionEnvioAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'tipo', 'estado', 'fecha_envio', 'intentos_envio']
    list_filter = ['tipo', 'estado', 'fecha_envio']
    search_fields = ['pedido__numero_pedido', 'destinatario_email']
    readonly_fields = ['creado_en', 'actualizado_en']
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.utils import timezone
from apps.Autenticacion.models import Usuario
from apps.Pedidos.models import Pedido, GuiaEnvio, Reclamo
from apps.Ubicaciones.models import Pais, Departamento, Ciudad, Hub


@login_required
def dashboard_principal_view(request):
    """Dashboard principal con KPIs y métricas del sistema"""
    
    # KPIs principales
    stats = {
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': Usuario.objects.filter(is_active=True).count(),
        'total_pedidos': Pedido.objects.count(),
        'pedidos_pendientes': Pedido.objects.filter(estado='BORRADOR').count(),  # FIX-05: BORRADOR es el estado inicial
        'pedidos_entregados': Pedido.objects.filter(estado='ENTREGADO').count(),
        'en_transito': Pedido.objects.filter(estado='EN_TRANSITO').count(),
        'total_guias': GuiaEnvio.objects.count(),
        'total_reclamos': Reclamo.objects.count(),
        'total_hubs': Hub.objects.count(),
        'total_paises': Pais.objects.count(),
        'total_departamentos': Departamento.objects.count(),
        'total_ciudades': Ciudad.objects.count(),
        'total_vehiculos': 0,  # Temporalmente 0 hasta que Rutas esté activo
        'total_rutas': 0,  # Temporalmente 0 hasta que Rutas esté activo
        'ingresos_totales': 0,  # Temporalmente 0 hasta que se implemente
        'pedidos_hoy': Pedido.objects.filter(fecha_pedido__date=timezone.now().date()).count(),
        'reclamos_pendientes': Reclamo.objects.filter(estado='RADICADO').count(),  # FIX-05: estado inicial = RADICADO
        'guias_activas': GuiaEnvio.objects.filter(estado='EN_CIRCULACION').count(),  # FIX-05: estado real = EN_CIRCULACION
        'hubs_activos': Hub.objects.filter(es_activo=True).count(),
        'pedidos_mes': Pedido.objects.filter(fecha_pedido__month=timezone.now().month, 
                                           fecha_pedido__year=timezone.now().year).count(),
        'reclamos_mes': Reclamo.objects.filter(creado_en__month=timezone.now().month,
                                             creado_en__year=timezone.now().year).count(),
        'tasa_entrega': 0,  # Se calculará dinámicamente
        'promedio_entrega': 0,  # Se calculará cuando tengamos datos
        'utilizacion_fleet': 0,  # Se calculará cuando Rutas esté activo
        'satisfaccion_cliente': 0,  # Pendiente implementar encuestas
        'costo_operativo': 0,  # Pendiente implementar cálculos
        'margen_profit': 0,  # Pendiente implementar cálculos
        'eficiencia_rutas': 0,  # Se calculará cuando Rutas esté activo
        'tiempo_respuesta': 0,  # Pendiente implementar métricas
        'disponibilidad_servicio': 95.5,  # Porcentaje de uptime
        'incidentes_criticos': Reclamo.objects.filter(prioridad='CRITICO').count(),
        'capacidad_almacenamiento': Hub.objects.aggregate(total=Sum('capacidad_operativa'))['total'] or 0,
        'ocupacion_almacenamiento': 0,  # Se calculará dinámicamente
        'pedidos_procesados': Pedido.objects.filter(estado__in=['ENTREGADO', 'CANCELADO']).count(),
        'reclamos_resueltos': Reclamo.objects.filter(estado__in=['APROBADO', 'PAGADO', 'CERRADO']).count(),  # FIX-05
        'usuarios_nuevos_mes': Usuario.objects.filter(created_at__month=timezone.now().month,
                                                     created_at__year=timezone.now().year).count(),
        'hubs_por_region': 0,  # Se calculará cuando tengamos datos regionales
        'rutas_optimizadas': 0,  # Se calculará cuando Rutas esté activo
        'entregas_puntuales': 0,  # Se calculará con datos de tiempo real
        'devoluciones': Pedido.objects.filter(estado='DEVUELTO').count(),
        'reembolsos': Reclamo.objects.filter(tipo='COBRANZA_INDEBIDA').count(),  
        'quejas_servicio': Reclamo.objects.filter(tipo='RETRASO').count(),            
        'danos_producto': Reclamo.objects.filter(tipo='DAÑO').count(),              
        'perdidas_envio': Reclamo.objects.filter(tipo='EXTRAVIO').count(),           
        'tiempo_promedio_entrega': 0,  
        'costo_promedio_envio': 0,    
        'productividad_mensajeros': 0,  
        'indice_satisfaccion': 0,  
        'tasa_retencion_clientes': 0,  
        'valor_pedido_promedio': 0,  
        'crecimiento_mensual': 0,  
        'metricas_calidad': 0,  # Se calculará con KPIs de calidad
        'performance_operativa': 0,  # Se calculará con métricas operativas
        'kpi_financieros': 0,  # Se calculará con datos financieros
        'indicadores_servicio': 0,  # Se calculará con métricas de servicio
    }
    
    # Calcular algunas métricas dinámicas
    if stats['total_pedidos'] > 0:
        stats['tasa_entrega'] = round((stats['pedidos_entregados'] / stats['total_pedidos']) * 100, 2)
    
    # Estadísticas por rol
    usuarios_por_rol = Usuario.objects.values('rol__tipo_rol').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.select_related(
        'usuario', 'tipo_servicio'
    ).order_by('-fecha_pedido')[:5]
    
    # Reclamos recientes
    reclamos_recientes = Reclamo.objects.select_related(
        'reclamante', 'pedido'
    ).order_by('-creado_en')[:5]
    
    # Distribución geográfica
    hubs_por_pais = Hub.objects.values('ciudad__departamento__pais__nombre').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Pedidos por estado para gráficos
    pedidos_por_estado = Pedido.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Reclamos por prioridad
    reclamos_por_prioridad = Reclamo.objects.values('prioridad').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Usuarios por mes (últimos 6 meses)
    from django.db.models.functions import TruncMonth
    usuarios_por_mes = Usuario.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')[:6]
    
    # ✅ Datos estructurados para el mapa interactivo (Pedidos activos geocodificados)
    pedidos_mapa = []
    pedidos_activos_query = Pedido.objects.exclude(estado='ENTREGADO')
    for p in pedidos_activos_query:
        if p.latitud_destino and p.longitud_destino:
            pedidos_mapa.append({
                'id': p.numero_pedido,
                'lat': float(p.latitud_destino),
                'lng': float(p.longitud_destino),
                'estado': p.estado,
                'cliente': p.nombre_destinatario
            })
            
    context = {
        # Datos para dashboard-admin.html
        'pedidos_mapa': pedidos_mapa, 
        'total_pedidos': stats['total_pedidos'],
        'en_transito': stats['en_transito'],
        'entregados': stats['pedidos_entregados'],
        'ingresos_totales': stats['ingresos_totales'],
        'total_vehiculos': stats['total_vehiculos'],
        'total_rutas': stats['total_rutas'],
        'total_usuarios': stats['total_usuarios'],
        
        # KPIs adicionales para expansion futura
        'stats': stats,
        'usuarios_por_rol': usuarios_por_rol,
        'pedidos_recientes': pedidos_recientes,
        'reclamos_recientes': reclamos_recientes,
        'hubs_por_pais': hubs_por_pais,
        'pedidos_por_estado': pedidos_por_estado,
        'reclamos_por_prioridad': reclamos_por_prioridad,
        'usuarios_por_mes': usuarios_por_mes,
        
        # KPIs específicos para módulos futuros
        'kpi_ubicaciones': {
            'total_paises': stats['total_paises'],
            'total_departamentos': stats['total_departamentos'],
            'total_ciudades': stats['total_ciudades'],
            'total_hubs': stats['total_hubs'],
            'hubs_activos': stats['hubs_activos'],
            'capacidad_total': stats['capacidad_almacenamiento'],
            'ocupacion': stats['ocupacion_almacenamiento'],
        },
        'kpi_pedidos': {
            'total': stats['total_pedidos'],
            'hoy': stats['pedidos_hoy'],
            'mes': stats['pedidos_mes'],
            'pendientes': stats['pedidos_pendientes'],
            'entregados': stats['pedidos_entregados'],
            'en_transito': stats['en_transito'],
            'tasa_entrega': stats['tasa_entrega'],
            'tiempo_promedio': stats['tiempo_promedio_entrega'],
        },
        'kpi_guias': {
            'total': stats['total_guias'],
            'activas': stats['guias_activas'],
            'generadas_hoy': 0,  # Se implementará
            'tracking_real': 0,  # Se implementará con GPS
        },
        'kpi_reclamos': {
            'total': stats['total_reclamos'],
            'pendientes': stats['reclamos_pendientes'],
            'criticos': stats['incidentes_criticos'],
            'resueltos': stats['reclamos_resueltos'],
            'mes': stats['reclamos_mes'],
            'devoluciones': stats['devoluciones'],
            'reembolsos': stats['reembolsos'],
            'quejas_servicio': stats['quejas_servicio'],
            'danos_producto': stats['danos_producto'],
            'perdidas_envio': stats['perdidas_envio'],
        },
        'kpi_financieros': {
            'ingresos_totales': stats['ingresos_totales'],
            'costo_operativo': stats['costo_operativo'],
            'margen_profit': stats['margen_profit'],
            'valor_pedido_promedio': stats['valor_pedido_promedio'],
            'costo_promedio_envio': stats['costo_promedio_envio'],
            'crecimiento_mensual': stats['crecimiento_mensual'],
        },
        'kpi_operacion': {
            'vehiculos': stats['total_vehiculos'],
            'rutas': stats['total_rutas'],
            'rutas_optimizadas': stats['rutas_optimizadas'],
            'utilizacion_fleet': stats['utilizacion_fleet'],
            'eficiencia_rutas': stats['eficiencia_rutas'],
            'productividad_mensajeros': stats['productividad_mensajeros'],
            'entregas_puntuales': stats['entregas_puntuales'],
        },
        'kpi_servicio': {
            'satisfaccion_cliente': stats['satisfaccion_cliente'],
            'tiempo_respuesta': stats['tiempo_respuesta'],
            'disponibilidad_servicio': stats['disponibilidad_servicio'],
            'indice_satisfaccion': stats['indice_satisfaccion'],
            'tasa_retencion': stats['tasa_retencion_clientes'],
            'metricas_calidad': stats['metricas_calidad'],
        },
        'kpi_usuarios': {
            'total': stats['total_usuarios'],
            'activos': stats['usuarios_activos'],
            'nuevos_mes': stats['usuarios_nuevos_mes'],
            'por_rol': usuarios_por_rol,
            'crecimiento': usuarios_por_mes,
        },
    }
    
    return render(request, 'dashboard/dashboard-admin.html', context)

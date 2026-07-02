from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse, FileResponse
from django.utils import timezone

from apps.Autenticacion.models import Usuario, Rol
from apps.Pedidos.models import Pedido, EstadoPedido, TipoServicio
from apps.Rutas.models import Vehiculo, Ruta

from apps.Autenticacion.forms import UsuarioForm
from apps.Pedidos.forms import PedidoForm, TipoServicioForm
from apps.Rutas.forms import VehiculoForm, RutaForm
import tablib
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


from apps.core.decorators import role_required, admin_required
from apps.Autenticacion.models import TipoRol

@admin_required
def dashboard(request):
    """Vista principal del dashboard administrativo."""
    # Obtener estados dinámicamente para evitar errores si no existen aún
    estado_transito = EstadoPedido.objects.filter(nombre__icontains='transito').first()
    estado_entregado = EstadoPedido.objects.filter(nombre__icontains='entregado').first()

    context = {
        'total_pedidos': Pedido.objects.count(),
        'en_transito': Pedido.objects.filter(estado=estado_transito).count() if estado_transito else 0,
        'entregados': Pedido.objects.filter(estado=estado_entregado).count() if estado_entregado else 0,
        'total_vehiculos': Vehiculo.objects.count(),
        'total_rutas': Ruta.objects.count(),
        'rutas_activas': Ruta.objects.filter(status_ruta='ACTIVA').count(),
        'total_usuarios': Usuario.objects.count(),
        'usuarios_activos': Usuario.objects.filter(is_active=True).count(),
        'pedidos_activos': Pedido.objects.exclude(estado=estado_entregado).count() if estado_entregado else 0,
        'ingresos_totales': Pedido.objects.aggregate(
            total=Sum('total_final')
        )['total'] or 0,
        'role': request.user.rol.tipo_rol if hasattr(request.user, 'rol') else 'N/A',
        'email': request.user.email,
    }
    
    # ✅ Datos estructurados para el mapa interactivo (Pedidos en tránsito/activos)
    pedidos_mapa = []
    pedidos_activos_query = Pedido.objects.exclude(estado=estado_entregado) if estado_entregado else Pedido.objects.all()
    for p in pedidos_activos_query:
        if p.latitud_destino and p.longitud_destino:
            pedidos_mapa.append({
                'id': p.numero_pedido,
                'lat': float(p.latitud_destino),
                'lng': float(p.longitud_destino),
                'estado': p.estado,
                'cliente': p.nombre_destinatario
            })
    context['pedidos_mapa'] = pedidos_mapa

    return render(request, 'dashboard/dashboard-admin.html', context)


@role_required(TipoRol.CLIENTE)
def dashboard_cliente(request):
    """Dashboard exclusivo para Clientes."""
    user = request.user
    pedidos = Pedido.objects.filter(usuario=user)
    context = {
        'total_pedidos': pedidos.count(),
        'en_transito': pedidos.filter(estado__in=[EstadoPedido.EN_TRANSITO, EstadoPedido.EN_RUTA]).count(),
        'entregados': pedidos.filter(estado=EstadoPedido.ENTREGADO).count(),
    }
    return render(request, 'dashboard/dashboard_cliente.html', context)


@role_required(TipoRol.MENSAJERO)
def dashboard_mensajero(request):
    """Dashboard exclusivo para Mensajeros (Conductores)."""
    user = request.user
    hoy = timezone.now().date()
    context = {
        'entregas_hoy': Pedido.objects.filter(mensajero=user, fecha_entrega__date=hoy).count(),
        'pendientes': Pedido.objects.filter(mensajero=user, estado=EstadoPedido.EN_RUTA).count(),
        'completadas': Pedido.objects.filter(mensajero=user, estado=EstadoPedido.ENTREGADO).count(),
        'rutas_activas': Ruta.objects.filter(conductor=user, estado='activa').count(),
    }
    return render(request, 'dashboard/dashboard_mensajero.html', context)


@role_required(TipoRol.PROVEEDOR)
def dashboard_proveedor(request):
    """Dashboard exclusivo para Proveedores."""
    context = {
        'nombre_proveedor': request.user.nombre_completo,
        'cotizaciones': 0,
        'pendientes': 0,
        'facturacion': 0,
    }
    return render(request, 'dashboard/dashboard_proveedor.html', context)


# ── Helpers de Exportación (Temporalmente aquí) ──

def render_to_pdf(headers, rows, title, filename):
    """Renderiza un dataset a un PDF con diseño premium de Enviart."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(A4), 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=40, 
        bottomMargin=30
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos
    system_name_style = styles['Normal'].clone('SystemName')
    system_name_style.alignment = 1
    system_name_style.fontSize = 8
    system_name_style.textColor = colors.grey
    system_name_style.letterSpacing = 1
    
    report_title_style = styles['Heading1'].clone('ReportTitle')
    report_title_style.alignment = 1
    report_title_style.fontSize = 24
    report_title_style.textColor = colors.HexColor('#2c3e50')
    
    meta_style = styles['Normal'].clone('Meta')
    meta_style.alignment = 1
    meta_style.fontSize = 10
    meta_style.textColor = colors.HexColor('#7f8c8d')
    
    # 1. Header
    elements.append(Paragraph("SISTEMA DE GESTIÓN DE ENVÍOS", system_name_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(title, report_title_style))
    
    # 2. Línea decorativa
    line_table = Table([['']], colWidths=['100%'])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 3, colors.HexColor('#3498db')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 15))
    
    # 3. Meta
    fecha = timezone.now().strftime('%d/%m/%Y')
    elements.append(Paragraph(f"Generado el: {fecha}", meta_style))
    elements.append(Paragraph(f"Total de registros: {len(rows)}", meta_style))
    elements.append(Spacer(1, 30))
    
    # Colores dinámicos para Estados y Roles (Rellenos suaves)
    color_map = {
        'Activo': colors.HexColor('#d4efdf'),        # Verde claro
        'Inactivo': colors.HexColor('#f9ebea'),       # Rojo claro
        'Administrador': colors.HexColor('#d6eaf8'),  # Azul claro
        'Cliente': colors.HexColor('#ebdef0'),        # Morado claro
        'Mensajero': colors.HexColor('#fef9e7'),       # Amarillo claro
        'Completada': colors.HexColor('#d4efdf'),     # Verde claro
        'Pendiente': colors.HexColor('#fef9e7'),      # Amarillo claro
        'En Curso': colors.HexColor('#d6eaf8'),       # Azul claro
        'Cancelada': colors.HexColor('#fadbd8'),      # Rojo salmón
    }

    processed_rows = []
    for row in rows:
        new_row = []
        for val in row:
            if str(val) in color_map:
                # Crear una mini-tabla para que el fondo solo ocupe el texto (Efecto Badge)
                badge = Table([[str(val).upper()]], hAlign='CENTER')
                badge.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), color_map[str(val)]),
                    ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                new_row.append(badge)
            else:
                new_row.append(val)
        processed_rows.append(new_row)

    # 4. Tabla
    data = [headers] + processed_rows
    
    # Calcular anchos dinámicamente para llenar la página
    # landscape(A4) es ~842 puntos de ancho
    page_width, page_height = landscape(A4) 
    available_width = page_width - doc.leftMargin - doc.rightMargin
    num_cols = len(headers)
    col_widths = [available_width / num_cols] * num_cols
    
    table = Table(data, repeatRows=1, colWidths=col_widths)
    
    table_style_list = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
    ]

    table.setStyle(TableStyle(table_style_list))
    elements.append(table)
    
    # 5. Footer
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Enviart - Sistema de Gestión de Envíos", meta_style))
    elements.append(Paragraph("Este documento fue generado automáticamente.", meta_style))
    
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=filename)


def export_dataset(dataset, file_format, base_filename):
    """Exporta un dataset de tablib al formato solicitado."""
    if file_format == 'xlsx':
        content = dataset.export('xlsx')
        response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.xlsx"'
        return response
    elif file_format == 'csv':
        content = dataset.export('csv')
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.csv"'
        return response
    elif file_format == 'json':
        content = dataset.export('json')
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.json"'
        return response
    return None


# ── Vehículos ── (Movido a apps.Rutas tras terminar Pedido)

# ── Rutas ── (Movido a apps.Rutas)


# ── Servicios ──

# ── Rutas ── (Movido a apps.Rutas tras terminar Pedido)

# ── Novedades ── (Movido a apps.Novedades tras Rutas)

# ── Modularización Completa

# ── Pagos ──

# ── CRUD Pedidos - Movido a apps.Pedido

# ── Fin de CRUD Pedidos

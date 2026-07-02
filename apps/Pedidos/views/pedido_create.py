from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from apps.Autenticacion.models import Usuario
from apps.Pedidos.models import Pedido, TipoServicio
from apps.Ubicaciones.models import Hub
from apps.Pedidos.forms import PedidoForm


@login_required
def pedido_create_view(request):
    """Vista para crear un nuevo pedido con diseño profesional"""
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        print(f"POST data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Form errors: {form.errors}")
        if form.is_valid():
            try:
                # Crear el pedido
                pedido = form.save(commit=False)
                pedido.usuario = request.user
                pedido.fecha_pedido = timezone.now()
                
                # Establecer estado inicial
                from ..models.choices import EstadoPedido
                pedido.estado = EstadoPedido.PENDIENTE_PAGO
                
                print(f"Pedido antes de save: usuario={pedido.usuario}, fecha={pedido.fecha_pedido}, estado={pedido.estado}")
                
                # Calcular costo automáticamente
                if pedido.peso_real_kg and pedido.valor_declarado:
                    from decimal import Decimal
                    costo_base = pedido.peso_real_kg * Decimal('5')  # $5 por kg
                    costo_seguro = pedido.valor_declarado * Decimal('0.01')  # 1% del valor
                    pedido.subtotal = costo_base + costo_seguro
                    pedido.total_final = pedido.subtotal  # Sin descuento ni impuestos por ahora
                    print(f"Costo calculado: base={costo_base}, seguro={costo_seguro}, subtotal={pedido.subtotal}")
                
                pedido.save()
                print(f"✅ Pedido guardado exitosamente: ID={pedido.id}")
                
                messages.success(request, f'Pedido #{pedido.id} creado exitosamente. Procede al pago seguro.')
                return redirect('checkout_pago', pedido_id=pedido.id)
                
            except Exception as e:
                import traceback
                print(f"❌ ERROR al guardar pedido: {str(e)}")
                print(traceback.format_exc())
                messages.error(request, f'Error al crear el pedido: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PedidoForm()
    
    # Obtener datos para el sidebar
    stats = {
        'total_pedidos': Pedido.objects.count(),
        'pedidos_hoy': Pedido.objects.filter(fecha_pedido__date=timezone.now().date()).count(),
        'hubs_activos': Hub.objects.filter(es_activo=True).count(),
        'tipos_servicio': TipoServicio.objects.all(),
    }
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Pedido',
        'button_text': 'Crear Pedido',
        'stats': stats,
    }
    
    return render(request, 'dashboard/pedido_create.html', context)


@login_required
def pedido_update_view(request, pedido_id):
    """Vista para editar un pedido existente"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos
    if not request.user.es_admin() and pedido.usuario != request.user:
        messages.error(request, 'No tienes permisos para editar este pedido.')
        return redirect('dashboard_pedidos')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            try:
                pedido = form.save(commit=False)
                
                # Recalcular costos
                if pedido.peso_real_kg and pedido.valor_declarado:
                    from decimal import Decimal
                    costo_base = pedido.peso_real_kg * Decimal('5')
                    costo_seguro = pedido.valor_declarado * Decimal('0.01')
                    pedido.subtotal = costo_base + costo_seguro
                    pedido.total_final = pedido.subtotal
                
                pedido.save()
                messages.success(request, f'Pedido #{pedido.id} actualizado exitosamente.')
                return redirect('dashboard_pedidos')
            except Exception as e:
                messages.error(request, f'Error al actualizar el pedido: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PedidoForm(instance=pedido)
    
    stats = {
        'total_pedidos': Pedido.objects.count(),
        'pedidos_hoy': Pedido.objects.filter(fecha_pedido__date=timezone.now().date()).count(),
        'hubs_activos': Hub.objects.filter(es_activo=True).count(),
        'tipos_servicio': TipoServicio.objects.all(),
    }
    
    context = {
        'form': form,
        'pedido': pedido,
        'title': f'Editar Pedido #{pedido.id}',
        'button_text': 'Guardar Cambios',
        'stats': stats,
    }
    
    return render(request, 'dashboard/pedido_create.html', context)


@login_required
def pedido_delete_view(request, pedido_id):
    """Vista para eliminar un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos - solo admins pueden eliminar
    if not request.user.es_admin():
        messages.error(request, 'No tienes permisos para eliminar pedidos.')
        return redirect('dashboard_pedidos')
    
    if request.method == 'POST':
        try:
            pedido_id = pedido.id
            pedido.delete()
            messages.success(request, f'Pedido #{pedido_id} eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el pedido: {str(e)}')
        return redirect('dashboard_pedidos')
    
    context = {
        'pedido': pedido,
        'title': f'Eliminar Pedido #{pedido.id}',
    }
    
    return render(request, 'dashboard/pedido_delete.html', context)


@login_required
def pedido_detail_view(request, pedido_id):
    """Vista para ver detalles de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos
    if not request.user.es_admin() and pedido.usuario != request.user:
        messages.error(request, 'No tienes permisos para ver este pedido.')
        return redirect('dashboard_pedidos')
    
    context = {
        'pedido': pedido,
        'title': f'Pedido #{pedido.id}',
    }
    
    return render(request, 'dashboard/pedido_detail.html', context)

import hashlib
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from apps.Pedidos.models import Pedido
from apps.Pedidos.models.pago import Pago
from apps.Pedidos.models.choices import EstadoPedido
from apps.Pedidos.services.wompi_service import get_wompi_service


def generar_firma_wompi(referencia, monto_centavos, moneda):
    """
    Genera la firma de integridad SHA-256 obligatoria para Wompi
    Fórmula: referencia + monto_en_centavos + moneda + secreto_integridad
    
    DEPRECATED: Use WompiService.generate_integrity_signature() instead
    """
    wompi_service = get_wompi_service()
    return wompi_service.generate_integrity_signature(referencia, monto_centavos, moneda)


from django.views.decorators.cache import never_cache

@login_required
@never_cache
def checkout_pago_view(request, pedido_id):
    """
    Vista de resumen del pedido donde se despliega el Widget de Wompi
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # 1. Seguridad: Evitar cobros dobles si el pedido ya fue pagado (cualquier estado avanzado)
    estados_pagados = [
        EstadoPedido.CONFIRMADO, EstadoPedido.EN_PREPARACION, EstadoPedido.RECOLECTADO,
        EstadoPedido.EN_HUB_ORIGEN, EstadoPedido.EN_TRANSITO, EstadoPedido.EN_HUB_DESTINO,
        EstadoPedido.EN_REPARTO, EstadoPedido.ENTREGADO
    ]
    if pedido.estado in estados_pagados:
        messages.success(request, f"El pedido #{pedido.numero_pedido} ya se encuentra pagado.")
        return redirect('dashboard_pedidos')
        
    # 2. Seguridad: Evitar cobros dobles si hay un pago en proceso en Wompi (ej. Nequi esperando confirmación)
    if pedido.pagos.filter(estado='PENDING').exists():
        messages.warning(request, f"El pedido #{pedido.numero_pedido} tiene un pago en proceso. Por favor espera unos minutos.")
        return redirect('dashboard_pedidos')
    # Get WOMPI service instance
    wompi_service = get_wompi_service()
    
    # Prepare checkout context
    context = wompi_service.prepare_checkout_context(
        pedido,
        request.build_absolute_uri
    )
    
    # Add DEBUG flag and checkout URL for template
    context['DEBUG'] = settings.DEBUG
    context['wompi_checkout_url'] = settings.WOMPI_CHECKOUT_URL
    
    # Log checkout attempt for debugging
    wompi_service.log_checkout_attempt(
        context['referencia'],
        context['monto_en_centavos'],
        context['firma']
    )
    
    return render(request, 'dashboard/checkout_pago.html', context)


@csrf_exempt
def wompi_webhook_view(request):
    """
    Endpoint que Wompi llama asíncronamente al actualizar la transacción.
    Valida firma de eventos para garantizar autenticidad.
    """
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)
        
    try:
        payload = json.loads(request.body)
        print("\n=== WEBHOOK WOMPI RECIBIDO ===")
        print(f"Evento: {payload.get('event')}")
        data_tx_log = payload.get('data', {}).get('transaction', {})
        print(f"  Status: {data_tx_log.get('status')}")
        print(f"  Reference: {data_tx_log.get('reference')}")
        print(f"  TX ID: {data_tx_log.get('id')}")
        print(f"  Amount: {data_tx_log.get('amount_in_cents')}")
        print("===============================\n")
        
        evento = payload.get('event')
        data_tx = payload.get('data', {}).get('transaction', {})
        
        # Get WOMPI service instance
        wompi_service = get_wompi_service()
        
        # 1. Validar la autenticidad del evento usando X-Event-Checksum (o signature)
        signature_obj = payload.get('signature', {})
        properties = signature_obj.get('properties', [])
        checksum_recibido = signature_obj.get('checksum')
        timestamp = payload.get('timestamp')
        
        # Concatenar propiedades dinámicas
        valores_propiedades = ""
        for prop in properties:
            # e.g., 'transaction.id' -> data_tx['id']
            parts = prop.split('.')
            if len(parts) == 2 and parts[0] == 'transaction':
                val = data_tx.get(parts[1])
                valores_propiedades += str(val)
                
        # Validate webhook signature
        is_valid, error_msg = wompi_service.validate_webhook_signature(
            checksum_recibido,
            valores_propiedades,
            timestamp
        )
        
        if not is_valid:
            # En modo sandbox, loguear el error pero continuar procesando
            # En producción, rechazar eventos con firma inválida
            print(f"⚠️ WEBHOOK: Firma inválida ({error_msg}). Modo: {wompi_service.mode}")
            if wompi_service.mode == 'production':
                return HttpResponse(f"Firma del webhook inválida: {error_msg}", status=401)
            
        # 2. Procesar la actualización si es evento de transacción
        if evento == 'transaction.updated':
            referencia = data_tx.get('reference')
            estado_wompi = data_tx.get('status')
            wompi_tx_id = data_tx.get('id')
            monto_centavos = data_tx.get('amount_in_cents')
            monto_pesos = monto_centavos / 100
            
            # Buscar el pedido a partir de la referencia (ej: PED-2026-000001-TX1-1717520000)
            pedido_id_str = referencia.split('-TX')[-1]
            pedido_id = pedido_id_str.split('-')[0]
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Guardar o actualizar registro de pago
            pago, created = Pago.objects.get_or_create(
                wompi_tx_id=wompi_tx_id,
                defaults={
                    'pedido': pedido,
                    'monto': monto_pesos,
                    'referencia': referencia,
                }
            )
            
            pago.estado = estado_wompi
            pago.detalles_adicionales = data_tx
            
            # Mapear método de pago al código correcto del modelo
            pago_method = data_tx.get('payment_method_type')
            metodo_map = {
                'CARD': 'TARJETA_CREDITO',
                'TRANSFER': 'PSE',
                'NEQUI': 'NEQUI',
                'DAVIPLATA': 'NEQUI',
                'BANCOLOMBIA_TRANSFER': 'BANCOLOMBIA_TRANSFER',
            }
            if pago_method:
                pago.metodo = metodo_map.get(pago_method, 'TARJETA_CREDITO')
            pago.save()
            
            # Actualizar estado de Pedido en función del pago
            nueva_estado = wompi_service.map_wompi_status_to_pedido_status(estado_wompi)
            if nueva_estado:
                pedido.estado = nueva_estado
                
                # Crear evento de tracking para estados de éxito
                if estado_wompi == 'APPROVED':
                    try:
                        from apps.Pedidos.models.tracking import EventoTracking
                        from apps.Pedidos.models.choices import TipoEventoTracking
                        EventoTracking.objects.create(
                            pedido=pedido,
                            tipo_evento=TipoEventoTracking.PEDIDO_CONFIRMADO,
                            ubicacion_texto=pedido.destino_completo,
                            descripcion=f"Pago aprobado exitosamente mediante Wompi (ID: {wompi_tx_id})"
                        )
                    except Exception as tracking_err:
                        print(f"⚠️ No se pudo crear EventoTracking: {tracking_err}")
                
                # Solo actualizar el campo estado, sin ejecutar geocodificación ni lógica costosa
                pedido.save(update_fields=['estado', 'actualizado_en'])
                print(f"✅ Pedido {pedido.id} actualizado a estado: {nueva_estado}")
            
        return HttpResponse("Evento procesado correctamente", status=200)
        
    except Pedido.DoesNotExist:
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR EN WEBHOOK WOMPI:")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)

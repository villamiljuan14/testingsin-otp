"""
Mock WOMPI Gateway para testing local
Simula el comportamiento de WOMPI sin necesidad de conexión externa
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import hashlib


@csrf_exempt
@require_http_methods(["POST", "GET"])
def mock_wompi_checkout(request):
    """
    Mock endpoint que simula el checkout de WOMPI
    Cuando en producción, será reemplazado por WOMPI real
    """
    if request.method == 'GET':
        # Mostrar formulario de pago mock
        reference = request.GET.get('reference', 'N/A')
        amount = request.GET.get('amount_in_cents', '0')
        
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WOMPI Mock Checkout</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; }}
                .container {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; }}
                .form-group {{ margin: 15px 0; }}
                label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
                input {{ width: 100%; padding: 8px; box-sizing: border-box; }}
                select {{ width: 100%; padding: 8px; box-sizing: border-box; }}
                button {{ background: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                .success {{ color: green; }}
                .warning {{ color: orange; padding: 10px; background: #fff3cd; border-radius: 5px; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 WOMPI Mock Checkout (Testing)</h1>
                <div class="warning">
                    ⚠️ Este es un simulador para testing local.<br>
                    En producción usarás WOMPI real.
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label>Referencia:</label>
                        <input type="text" name="reference" value="{reference}" readonly>
                    </div>
                    
                    <div class="form-group">
                        <label>Monto:</label>
                        <input type="text" name="amount" value="${{amount/100:,.2f}} COP" readonly>
                    </div>
                    
                    <div class="form-group">
                        <label>Estado de la transacción:</label>
                        <select name="status">
                            <option value="APPROVED">✅ APROBADO (pago exitoso)</option>
                            <option value="DECLINED">❌ RECHAZADO (pago fallido)</option>
                            <option value="PENDING">⏳ PENDIENTE</option>
                        </select>
                    </div>
                    
                    <input type="hidden" name="amount_in_cents" value="{amount}">
                    <input type="hidden" name="redirect_url" value="{request.GET.get('redirect_url', '/dashboard/pedidos/')}">
                    
                    <button type="submit">Procesar Pago Mock</button>
                </form>
            </div>
        </body>
        </html>
        """)
    
    else:  # POST
        # Procesar mock de pago
        reference = request.POST.get('reference')
        status = request.POST.get('status', 'APPROVED')
        amount_in_cents = int(request.POST.get('amount_in_cents', 0))
        redirect_url = request.POST.get('redirect_url', '/dashboard/pedidos/')
        
        # Simular respuesta de WOMPI
        response_data = {
            'id': f'mock_{reference}',
            'reference': reference,
            'status': status,
            'amount_in_cents': amount_in_cents,
            'payment_method_type': 'CARD',
            'message': f'Mock Transaction {status}'
        }
        
        # Determinar clase CSS según estado
        css_class = 'success' if status == 'APPROVED' else 'declined'
        title = '✅ ¡Pago Exitoso!' if status == 'APPROVED' else '❌ Pago Rechazado'
        monto_formateado = f"{amount_in_cents/100:,.2f}"
        
        # Redirigir con parámetros (en WOMPI real, esto sería manejado por webhook)
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Resultado del Pago</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; text-align: center; }}
                .success {{ color: green; font-size: 24px; }}
                .declined {{ color: red; font-size: 24px; }}
            </style>
        </head>
        <body>
            <h1 class="{css_class}">
                {title}
            </h1>
            <p>Referencia: {reference}</p>
            <p>Estado: {status}</p>
            <p>Monto: ${monto_formateado} COP</p>
            <br>
            <p>Redirigiendo...</p>
            <script>
                setTimeout(() => {{
                    window.location.href = '{redirect_url}';
                }}, 3000);
            </script>
        </body>
        </html>
        """)


@csrf_exempt
def mock_wompi_widget_script(request):
    """
    Mock script que simula el widget de WOMPI
    """
    return HttpResponse("""
    console.log('🧪 WOMPI Mock Widget Loaded');
    
    window.WidgetCheckout = function(config) {
        this.config = config;
        this.open = function(callback) {
            console.log('🧪 Mock Wompi Checkout abierto con config:', this.config);
            // Redirigir al mock checkout pasandole los parámetros por URL
            var url = '/mock/wompi/checkout/?reference=' + encodeURIComponent(this.config.reference) + 
                      '&amount_in_cents=' + encodeURIComponent(this.config.amountInCents) +
                      '&redirect_url=' + encodeURIComponent(this.config.redirectUrl);
            window.location.href = url;
        };
    };analzia mi pyoecto y
    """, content_type='application/javascript')
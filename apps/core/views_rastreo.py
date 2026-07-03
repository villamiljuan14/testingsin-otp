from django.shortcuts import render
from apps.Pedidos.models import Pedido, GuiaEnvio, EventoTracking


def rastreo_publico_view(request):
    guia = request.GET.get('guia', '').strip()
    pedido = None
    eventos = []
    hay_mas = False
    total_eventos = 0
    error = None

    if guia:
        # Buscar por código de rastreo
        pedido = Pedido.objects.filter(codigo_rastreo__iexact=guia).first()
        # Buscar por número de pedido
        if not pedido:
            pedido = Pedido.objects.filter(numero_pedido__iexact=guia).first()
        # Buscar por número de guía física (GUI-...)
        if not pedido:
            guia_obj = GuiaEnvio.objects.filter(numero_guia__iexact=guia).first()
            if guia_obj and guia_obj.pedido:
                pedido = guia_obj.pedido

        if pedido:
            todos_eventos = list(
                EventoTracking.objects
                .filter(pedido=pedido)
                .select_related('hub', 'registrado_por')
                .order_by('fecha_registro')
            )
            total_eventos = len(todos_eventos)
            eventos = todos_eventos[:3]
            hay_mas = total_eventos > 3
        else:
            eventos = []
            hay_mas = False
            total_eventos = 0
            error = "No encontramos ningún envío con la guía proporcionada. Por favor verifica e intenta de nuevo."

    context = {
        'guia': guia,
        'pedido': pedido,
        'eventos': eventos,
        'hay_mas': hay_mas,
        'total_eventos': total_eventos,
        'error': error,
    }
    return render(request, 'rastreo.html', context)


def contacto_view(request):
    mensaje_enviado = False
    if request.method == 'POST':
        # En producción aquí iría el envío real de email
        # Por ahora solo marcamos el flag para mostrar el mensaje de éxito
        mensaje_enviado = True
    return render(request, 'contacto.html', {'mensaje_enviado': mensaje_enviado})

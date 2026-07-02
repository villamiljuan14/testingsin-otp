from django.shortcuts import render
from apps.Pedidos.models import Pedido, GuiaEnvio

def rastreo_publico_view(request):
    guia = request.GET.get('guia', '').strip()
    pedido = None
    error = None

    if guia:
        # Intentar buscar por código de rastreo (público) o por número de pedido
        pedido = Pedido.objects.filter(codigo_rastreo__iexact=guia).first()
        if not pedido:
            pedido = Pedido.objects.filter(numero_pedido__iexact=guia).first()
            
        # Intentar buscar por número de guía física (GUI-...)
        if not pedido:
            guia_obj = GuiaEnvio.objects.filter(numero_guia__iexact=guia).first()
            if guia_obj and guia_obj.pedido:
                pedido = guia_obj.pedido
                
        if not pedido:
            error = "No encontramos ningún envío con la guía proporcionada. Por favor verifica e intenta de nuevo."

    context = {
        'guia': guia,
        'pedido': pedido,
        'error': error
    }
    return render(request, 'rastreo.html', context)

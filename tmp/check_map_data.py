import os
import sys
import django

# Añadir el directorio raíz al path de Python
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.Pedidos.models import Pedido
from apps.Ubicaciones.models import Ciudad

def diagnostic():
    total_pedidos = Pedido.objects.count()
    pedidos_con_ciudad = Pedido.objects.filter(ciudad_destino__isnull=False).count()
    
    ciudades_con_coords = Ciudad.objects.filter(latitud__isnull=False, longitud__isnull=False).count()
    total_ciudades = Ciudad.objects.count()
    
    # Detalle de pedidos activos (no entregados) y sus coordenadas
    pedidos_activos = Pedido.objects.exclude(estado='ENTREGADO')
    validos_para_mapa = 0
    muestras = []
    
    for p in pedidos_activos:
        if p.ciudad_destino and p.ciudad_destino.latitud and p.ciudad_destino.longitud:
            validos_para_mapa += 1
            if len(muestras) < 5:
                muestras.append(f"{p.numero_pedido}: {p.ciudad_destino.nombre} ({p.ciudad_destino.latitud}, {p.ciudad_destino.longitud})")

    print(f"--- DIAGNÓSTICO DE DATOS PARA MAPA ---")
    print(f"Total Pedidos en Base de Datos: {total_pedidos}")
    print(f"Pedidos con Ciudad de Destino asignada: {pedidos_con_ciudad}")
    print(f"Pedidos activos (No Entregados): {pedidos_activos.count()}")
    print(f"---")
    print(f"Ciudades totales en sistema: {total_ciudades}")
    print(f"Ciudades con coordenadas (Lat/Lon): {ciudades_con_coords}")
    print(f"---")
    print(f"RESULTADO: {validos_para_mapa} pedidos listos para mostrarse en el mapa.")
    if muestras:
        print("Ejemplos:")
        for m in muestras:
            print(f" - {m}")
    else:
        print("ALERTA: Ningún pedido tiene coordenadas actualmente.")

if __name__ == "__main__":
    diagnostic()

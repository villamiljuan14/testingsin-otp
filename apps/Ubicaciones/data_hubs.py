# -*- coding: utf-8 -*-
"""
Comando para poblar tabla de Hubs con datos iniciales.
Ejecutar en shell de Django: exec(open('apps/Ubicaciones/data_hubs.py', encoding='utf-8').read())
"""

from apps.Ubicaciones.models import Hub, Ciudad

def poblar_hubs():
    """Crear hubs de ejemplo para Colombia"""
    
    # Obtener ciudades principales
    try:
        bogota = Ciudad.objects.get(nombre='Bogotá')
        medellin = Ciudad.objects.get(nombre='Medellín')
        cali = Ciudad.objects.get(nombre='Cali')
        barranquilla = Ciudad.objects.get(nombre='Barranquilla')
        cartagena = Ciudad.objects.get(nombre='Cartagena')
        bucaramanga = Ciudad.objects.get(nombre='Bucaramanga')
    except Ciudad.DoesNotExist as e:
        print(f"⚠️ Ciudad no encontrada: {e}")
        print("⚠️ Ejecuta primero: exec(open('apps/Ubicaciones/data_initial.py', encoding='utf-8').read())")
        return
    
    # Datos de hubs
    hubs_data = [
        {
            'nombre': 'Hub Principal Bogotá',
            'codigo_hub': 'HUB-BOG-01',
            'ciudad': bogota,
            'direccion': 'Calle 26 # 68-70, Zona Industrial',
            'telefono': '+57 601 1234567',
            'email_contacto': 'bogota@enviart.com',
            'tipo_hub': 'PRINCIPAL',
            'capacidad_operativa': 50000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Norte Bogotá',
            'codigo_hub': 'HUB-BOG-02',
            'ciudad': bogota,
            'direccion': 'Autopista Norte # 106-28, Usaquén',
            'telefono': '+57 601 7654321',
            'email_contacto': 'norte@enviart.com',
            'tipo_hub': 'SECUNDARIO',
            'capacidad_operativa': 25000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Medellín',
            'codigo_hub': 'HUB-MED-01',
            'ciudad': medellin,
            'direccion': 'Carrera 48 # 26-85, Belén',
            'telefono': '+57 604 1234567',
            'email_contacto': 'medellin@enviart.com',
            'tipo_hub': 'PRINCIPAL',
            'capacidad_operativa': 40000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Cali',
            'codigo_hub': 'HUB-CAL-01',
            'ciudad': cali,
            'direccion': 'Calle 5 # 38-28, Normandía',
            'telefono': '+57 602 1234567',
            'email_contacto': 'cali@enviart.com',
            'tipo_hub': 'PRINCIPAL',
            'capacidad_operativa': 35000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Barranquilla',
            'codigo_hub': 'HUB-BAR-01',
            'ciudad': barranquilla,
            'direccion': 'Calle 30 # 8-47, Centro',
            'telefono': '+57 605 1234567',
            'email_contacto': 'barranquilla@enviart.com',
            'tipo_hub': 'SECUNDARIO',
            'capacidad_operativa': 25000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Cartagena',
            'codigo_hub': 'HUB-CTG-01',
            'ciudad': cartagena,
            'direccion': 'Av. Pedro de Heredia # 15-27, Manga',
            'telefono': '+57 605 7654321',
            'email_contacto': 'cartagena@enviart.com',
            'tipo_hub': 'TEMPORAL',
            'capacidad_operativa': 15000,
            'es_activo': True
        },
        {
            'nombre': 'Hub Bucaramanga',
            'codigo_hub': 'HUB-BUC-01',
            'ciudad': bucaramanga,
            'direccion': 'Calle 33 # 18-24, Centro',
            'telefono': '+57 607 1234567',
            'email_contacto': 'bucaramanga@enviart.com',
            'tipo_hub': 'SECUNDARIO',
            'capacidad_operativa': 20000,
            'es_activo': True
        },
    ]
    
    for hub_data in hubs_data:
        hub, created = Hub.objects.get_or_create(
            codigo_hub=hub_data['codigo_hub'],
            defaults=hub_data
        )
        if created:
            print(f"✅ Creado: {hub.nombre} ({hub.codigo_hub})")
        else:
            print(f"ℹ️ Ya existe: {hub.nombre} ({hub.codigo_hub})")
    
    # Resumen
    print("\n📊 RESUMEN HUBS:")
    print(f"Total hubs: {Hub.objects.count()}")
    print(f"Hubs activos: {Hub.objects.filter(es_activo=True).count()}")
    print(f"Hubs inactivos: {Hub.objects.filter(es_activo=False).count()}")
    print("\n✅ Hubs cargados correctamente!")

if __name__ == '__main__':
    poblar_hubs()

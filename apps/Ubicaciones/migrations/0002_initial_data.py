# Generated manually - Initial data for Ubicaciones
from django.db import migrations

def crear_ubicaciones(apps, schema_editor):
    """
    Crear datos iniciales de ubicaciones para Colombia
    """
    Pais = apps.get_model('Ubicaciones', 'Pais')
    Departamento = apps.get_model('Ubicaciones', 'Departamento')
    Ciudad = apps.get_model('Ubicaciones', 'Ciudad')
    
    # Crear Colombia
    colombia, _ = Pais.objects.get_or_create(
        codigo_iso2='CO',
        defaults={
            'nombre': 'Colombia',
            'nombre_corto': 'Colombia',
            'codigo_iso3': 'COL',
            'codigo_telefono': '+57',
            'moneda': 'COP',
            'requiere_departamento': True,
            'requiere_codigo_postal': True,
            'es_activo': True
        }
    )
    
    # Departamentos
    deptos_data = [
        ('BOG', 'Bogotá D.C.'),
        ('ANT', 'Antioquia'),
        ('VLL', 'Valle del Cauca'),
        ('ATL', 'Atlántico'),
        ('SAN', 'Santander'),
        ('CUN', 'Cundinamarca'),
        ('BOL', 'Bolívar'),
        ('MET', 'Meta'),
        ('RIS', 'Risaralda'),
        ('CAL', 'Caldas'),
        ('QUI', 'Quindío'),
        ('TOL', 'Tolima'),
        ('HUI', 'Huila'),
        ('CAU', 'Cauca'),
        ('NAR', 'Nariño'),
        ('BOY', 'Boyacá'),
        ('CES', 'Cesar'),
        ('MAG', 'Magdalena'),
        ('SUC', 'Sucre'),
        ('COR', 'Córdoba'),
    ]
    
    deptos_map = {}
    for codigo, nombre in deptos_data:
        depto, _ = Departamento.objects.get_or_create(
            codigo=codigo,
            pais=colombia,
            defaults={'nombre': nombre, 'es_activo': True}
        )
        deptos_map[codigo] = depto
    
    # Ciudades principales
    ciudades_data = [
        ('Bogotá', 'BOG'),
        ('Medellín', 'ANT'),
        ('Cali', 'VLL'),
        ('Barranquilla', 'ATL'),
        ('Bucaramanga', 'SAN'),
        ('Cartagena', 'BOL'),
        ('Villavicencio', 'MET'),
        ('Pereira', 'RIS'),
        ('Manizales', 'CAL'),
        ('Armenia', 'QUI'),
        ('Ibagué', 'TOL'),
        ('Neiva', 'HUI'),
        ('Popayán', 'CAU'),
        ('Pasto', 'NAR'),
        ('Tunja', 'BOY'),
        ('Valledupar', 'CES'),
        ('Santa Marta', 'MAG'),
        ('Sincelejo', 'SUC'),
        ('Montería', 'COR'),
    ]
    
    for nombre, depto_codigo in ciudades_data:
        Ciudad.objects.get_or_create(
            nombre=nombre,
            departamento=deptos_map[depto_codigo],
            defaults={'es_activo': True}
        )

def crear_hubs(apps, schema_editor):
    """
    Crear hubs de ejemplo
    """
    Hub = apps.get_model('Ubicaciones', 'Hub')
    Ciudad = apps.get_model('Ubicaciones', 'Ciudad')
    
    # Obtener ciudades
    ciudades_map = {}
    for ciudad in Ciudad.objects.filter(nombre__in=['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga']):
        ciudades_map[ciudad.nombre] = ciudad
    
    hubs_data = [
        ('Hub Principal Bogotá', 'HUB-BOG-01', 'Bogotá', 'PRINCIPAL', 50000),
        ('Hub Norte Bogotá', 'HUB-BOG-02', 'Bogotá', 'SECUNDARIO', 25000),
        ('Hub Medellín', 'HUB-MED-01', 'Medellín', 'PRINCIPAL', 40000),
        ('Hub Cali', 'HUB-CAL-01', 'Cali', 'PRINCIPAL', 35000),
        ('Hub Barranquilla', 'HUB-BAR-01', 'Barranquilla', 'SECUNDARIO', 25000),
        ('Hub Cartagena', 'HUB-CTG-01', 'Cartagena', 'TEMPORAL', 15000),
        ('Hub Bucaramanga', 'HUB-BUC-01', 'Bucaramanga', 'SECUNDARIO', 20000),
    ]
    
    for nombre, codigo, ciudad_nombre, tipo, capacidad in hubs_data:
        if ciudad_nombre in ciudades_map:
            Hub.objects.get_or_create(
                codigo_hub=codigo,
                defaults={
                    'nombre': nombre,
                    'ciudad': ciudades_map[ciudad_nombre],
                    'tipo_hub': tipo,
                    'direccion': f'Dirección {nombre}',
                    'capacidad_operativa': capacidad,
                    'es_activo': True
                }
            )

class Migration(migrations.Migration):
    dependencies = [
        ('Ubicaciones', '0002_hub'),
    ]
    
    operations = [
        migrations.RunPython(crear_ubicaciones, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(crear_hubs, reverse_code=migrations.RunPython.noop),
    ]

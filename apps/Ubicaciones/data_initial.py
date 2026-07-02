# -*- coding: utf-8 -*-
"""
Comando para poblar tablas de ubicaciones con datos iniciales.
Ejecutar: python manage.py shell < apps/Ubicaciones/data_initial.py
"""

from apps.Ubicaciones.models import Pais, Departamento, Ciudad

def poblar_ubicaciones():
    """Poblar tablas de ubicaciones con datos básicos de Colombia"""
    
    # Crear Colombia si no existe
    colombia, created = Pais.objects.get_or_create(
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
    if created:
        print(f"✅ Creado: {colombia.nombre}")
    else:
        print(f"ℹ️ Ya existe: {colombia.nombre}")
    
    # Departamentos de Colombia
    departamentos_data = [
        ('BOG', 'Bogotá D.C.', '11001'),
        ('ANT', 'Antioquia', '05001'),
        ('VLL', 'Valle del Cauca', '76001'),
        ('ATL', 'Atlántico', '08001'),
        ('SAN', 'Santander', '68001'),
        ('CUN', 'Cundinamarca', '25001'),
        ('BOL', 'Bolívar', '13001'),
        ('MET', 'Meta', '50001'),
        ('RIS', 'Risaralda', '66001'),
        ('CAL', 'Caldas', '17001'),
        ('QUI', 'Quindío', '63001'),
        ('TOL', 'Tolima', '73001'),
        ('HUI', 'Huila', '41001'),
        ('CAU', 'Cauca', '19001'),
        ('NAR', 'Nariño', '52001'),
        ('BOY', 'Boyacá', '15001'),
        ('CES', 'Cesar', '20001'),
        ('MAG', 'Magdalena', '47001'),
        ('SUC', 'Sucre', '70001'),
        ('COR', 'Córdoba', '23001'),
    ]
    
    for codigo, nombre, _ in departamentos_data:
        depto, created = Departamento.objects.get_or_create(
            codigo=codigo,
            pais=colombia,
            defaults={
                'nombre': nombre,
                'es_activo': True
            }
        )
        if created:
            print(f"  ✅ Departamento: {depto.nombre}")
    
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
        try:
            depto = Departamento.objects.get(codigo=depto_codigo, pais=colombia)
            ciudad, created = Ciudad.objects.get_or_create(
                nombre=nombre,
                departamento=depto,
                defaults={
                    'es_activo': True,
                    'es_capital': (nombre in ['Bogotá', 'Medellín', 'Cali', 'Barranquilla'])
                }
            )
            if created:
                print(f"    ✅ Ciudad: {ciudad.nombre}")
        except Departamento.DoesNotExist:
            print(f"    ⚠️ Departamento no encontrado: {depto_codigo}")
    
    # Resumen
    print("\n📊 RESUMEN:")
    print(f"Países: {Pais.objects.count()}")
    print(f"Departamentos: {Departamento.objects.count()}")
    print(f"Ciudades: {Ciudad.objects.count()}")
    print("\n✅ Datos de ubicaciones cargados correctamente!")

if __name__ == '__main__':
    poblar_ubicaciones()

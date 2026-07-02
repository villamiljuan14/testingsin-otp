# apps/Ubicaciones/management/commands/cargar_colombia.py

from django.core.management.base import BaseCommand
from apps.Ubicaciones.models import Pais, Departamento, Ciudad


class Command(BaseCommand):
    help = 'Carga datos de Colombia'
    
    def handle(self, *args, **kwargs):
        # ✅ Crear país
        colombia, _ = Pais.objects.get_or_create(
            codigo_iso2='CO',
            defaults={
                'nombre': 'Colombia',
                'nombre_corto': 'Colombia',
                'codigo_iso3': 'COL',
                'codigo_telefono': '+57',
                'moneda': 'COP',
            }
        )
        
        # ✅ Crear departamentos
        departamentos = [
            {'nombre': 'Bogotá D.C.', 'codigo': 'DC', 'capital': 'Bogotá'},
            {'nombre': 'Antioquia', 'codigo': 'ANT', 'capital': 'Medellín'},
            {'nombre': 'Valle del Cauca', 'codigo': 'VAC', 'capital': 'Cali'},
            {'nombre': 'Cundinamarca', 'codigo': 'CUN', 'capital': 'Bogotá'},
            # ... más departamentos
        ]
        
        for dep_data in departamentos:
            departamento, _ = Departamento.objects.get_or_create(
                pais=colombia,
                nombre=dep_data['nombre'],
                defaults={
                    'codigo': dep_data['codigo'],
                    'capital': dep_data['capital'],
                }
            )
            
            # ✅ Crear ciudades principales
            ciudades = self.get_ciudades_por_departamento(dep_data['nombre'])
            for ciudad_nombre in ciudades:
                Ciudad.objects.get_or_create(
                    departamento=departamento,
                    nombre=ciudad_nombre,
                    defaults={'es_activo': True}
                )
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de Colombia cargados'))
    
    def get_ciudades_por_departamento(self, departamento):
        """Retorna lista de ciudades por departamento"""
        data = {
            'Bogotá D.C.': ['Bogotá'],
            'Antioquia': ['Medellín', 'Bello', 'Itagüí', 'Envigado'],
            'Valle del Cauca': ['Cali', 'Palmira', 'Buga', 'Tuluá'],
            'Cundinamarca': ['Soacha', 'Facatativá', 'Zipaquirá', 'Chía'],
        }
        return data.get(departamento, [])
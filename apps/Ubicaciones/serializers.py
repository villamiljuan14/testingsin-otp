from rest_framework import serializers
from .models import Pais, Departamento, Ciudad, Hub


class PaisSerializer(serializers.ModelSerializer):
    """Serializer para países"""
    class Meta:
        model = Pais
        fields = [
            'id', 'nombre', 'codigo_iso', 'codigo_iso3',
            'codigo_telefonico', 'moneda', 'idioma_principal',
            'zona_horaria', 'es_activo', 'nombre_completo'
        ]


class DepartamentoSerializer(serializers.ModelSerializer):
    """Serializer para departamentos"""
    class Meta:
        model = Departamento
        fields = [
            'id', 'nombre', 'codigo_dane', 'codigo_divipola',
            'region', 'pais', 'es_activo'
        ]
        depth = 1


class CiudadSerializer(serializers.ModelSerializer):
    """Serializer para ciudades"""
    class Meta:
        model = Ciudad
        fields = [
            'id', 'nombre', 'codigo_postal', 'latitud', 'longitud',
            'altitud', 'zona_postal', 'area_urbana', 'departamento',
            'es_activo', 'nombre_completo', 'coordenadas'
        ]
        depth = 2


class HubSerializer(serializers.ModelSerializer):
    """Serializer para hubs"""
    class Meta:
        model = Hub
        fields = [
            'id', 'nombre', 'codigo_hub', 'tipo_hub', 'ciudad',
            'direccion', 'telefono', 'email_contacto', 'latitud', 'longitud',
            'capacidad_operativa', 'horario_operacion', 'servicios_disponibles',
            'es_activo', 'direccion_completa'
        ]
        depth = 2
    
    def validate_capacidad_operativa(self, value):
        """Validar capacidad mínima"""
        if value < 100:
            raise serializers.ValidationError('La capacidad mínima es 100 paquetes')
        return value

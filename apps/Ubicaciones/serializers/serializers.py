from rest_framework import serializers
from .models import Pais, Departamento, Ciudad


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre', 'nombre_corto', 'codigo_iso2', 'codigo_telefono', 'moneda']


class DepartamentoSerializer(serializers.ModelSerializer):
    pais = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'codigo', 'pais', 'capital']


class CiudadSerializer(serializers.ModelSerializer):
    departamento = serializers.StringRelatedField(read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'departamento', 'codigo_postal', 'zona_envio', 'nombre_completo']


class CiudadConDependenciaSerializer(serializers.ModelSerializer):
    """Serializer para selectores en cascada"""
    departamento_id = serializers.PrimaryKeyRelatedField(
        source='departamento',
        queryset=Departamento.objects.all(),
        write_only=True
    )
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    pais_id = serializers.PrimaryKeyRelatedField(
        source='departamento.pais',
        read_only=True
    )
    pais_nombre = serializers.CharField(source='departamento.pais.nombre', read_only=True)
    
    class Meta:
        model = Ciudad
        fields = [
            'id', 'nombre', 'departamento_id', 'departamento_nombre',
            'pais_id', 'pais_nombre', 'codigo_postal', 'zona_envio'
        ]
from rest_framework import serializers
from ..models import AccionCorrectiva, Novedad


class AccionCorrectivaSerializer(serializers.ModelSerializer):
    """Serializer para acciones correctivas"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    responsable = serializers.StringRelatedField(read_only=True)
    verificada_por = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AccionCorrectiva
        fields = '__all__'
        read_only_fields = ['fecha_asignacion', 'creado_en', 'actualizado_en']


class AccionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear acciones correctivas"""
    
    class Meta:
        model = AccionCorrectiva
        fields = [
            'novedad', 'tipo', 'descripcion', 'responsable',
            'fecha_limite', 'costo_estimado',
        ]
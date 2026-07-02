from rest_framework import serializers
from ..models import TipoServicio


class TipoServicioSerializer(serializers.ModelSerializer):
    """Serializer para tipos de servicio"""
    
    class Meta:
        model = TipoServicio
        fields = '__all__'
        read_only_fields = ['creado_en', 'actualizado_en']
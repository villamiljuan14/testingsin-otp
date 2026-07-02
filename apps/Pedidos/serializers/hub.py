from rest_framework import serializers
from ..models import Hub


class HubSerializer(serializers.ModelSerializer):
    """Serializer para hubs"""
    
    hub_padre = serializers.StringRelatedField(read_only=True)
    es_hub_central = serializers.ReadOnlyField()
    
    class Meta:
        model = Hub
        fields = '__all__'
        read_only_fields = ['creado_en', 'actualizado_en']
from rest_framework import serializers
from ..models import MetricaNovedad


class MetricaNovedadSerializer(serializers.ModelSerializer):
    """Serializer para métricas de novedades"""
    
    class Meta:
        model = MetricaNovedad
        fields = '__all__'
        read_only_fields = ['fecha_calculo']
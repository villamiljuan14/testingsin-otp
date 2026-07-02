from rest_framework import serializers
from ..models import EvidenciaNovedad, Novedad


class EvidenciaNovedadSerializer(serializers.ModelSerializer):
    """Serializer para evidencias de novedad"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    subido_por = serializers.StringRelatedField(read_only=True)
    archivo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EvidenciaNovedad
        fields = '__all__'
        read_only_fields = ['creado_en', 'tamaño_bytes', 'nombre_original']
    
    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None


class EvidenciaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear evidencias"""
    
    class Meta:
        model = EvidenciaNovedad
        fields = [
            'novedad', 'tipo', 'archivo', 'descripcion',
            'latitud', 'longitud', 'fecha_captura',
        ]
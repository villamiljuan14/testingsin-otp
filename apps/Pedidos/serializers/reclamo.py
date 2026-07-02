from rest_framework import serializers
from ..models import Reclamo, Pedido


class ReclamoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reclamos"""
    
    pedido_id = serializers.PrimaryKeyRelatedField(
        queryset=Pedido.objects.all(),
        source='pedido',
        write_only=True
    )
    
    class Meta:
        model = Reclamo
        fields = [
            'pedido_id',
            'tipo',
            'prioridad',
            'descripcion',
            'descripcion_danos',
            'valor_reclamado',
            'documentos',
        ]
    
    def validate_pedido_id(self, value):
        """Validar que el pedido pueda tener reclamo"""
        if value.estado not in ['ENTREGADO', 'DEVUELTO', 'INTENTO_FALLIDO']:
            raise serializers.ValidationError(
                'Solo se pueden crear reclamos para pedidos entregados o devueltos'
            )
        return value
    
    def create(self, validated_data):
        """Crea el reclamo con datos del usuario actual"""
        request = self.context.get('request')
        
        validated_data['reclamante'] = request.user
        validated_data['nombre_reclamante'] = request.user.nombre_completo
        validated_data['email_reclamante'] = request.user.email
        validated_data['telefono_reclamante'] = request.user.telefono or ''
        
        return super().create(validated_data)


class ReclamoSerializer(serializers.ModelSerializer):
    """Serializer completo para reclamos"""
    
    pedido = serializers.StringRelatedField(read_only=True)
    reclamante = serializers.StringRelatedField(read_only=True)
    asignado_a = serializers.StringRelatedField(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Reclamo
        fields = '__all__'
        read_only_fields = [
            'numero_reclamo', 'reclamante', 'nombre_reclamante',
            'email_reclamante', 'telefono_reclamante', 'fecha_radicacion',
            'fecha_limite_respuesta', 'estado', 'creado_en', 'actualizado_en'
        ]
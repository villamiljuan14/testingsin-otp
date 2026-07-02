from rest_framework import serializers
from ..models import GuiaEnvio, Pedido


class GuiaCreateSerializer(serializers.ModelSerializer):
    """Serializer para generar guía"""
    
    pedido_id = serializers.PrimaryKeyRelatedField(
        queryset=Pedido.objects.all(),
        source='pedido',
        write_only=True
    )
    
    class Meta:
        model = GuiaEnvio
        fields = [
            'pedido_id',
            'instrucciones_especiales',
            'es_fragil',
            'requiere_firma',
            'no_doblar',
        ]
    
    def validate_pedido_id(self, value):
        """Validar que el pedido pueda tener guía"""
        if value.estado not in ['CONFIRMADO', 'EN_PREPARACION']:
            raise serializers.ValidationError(
                f'El pedido debe estar CONFIRMADO o EN_PREPARACION (estado actual: {value.estado})'
            )
        
        if hasattr(value, 'guia'):
            raise serializers.ValidationError('El pedido ya tiene una guía generada')
        
        return value
    
    def create(self, validated_data):
        """Crea la guía con datos del pedido"""
        pedido = validated_data['pedido']
        
        validated_data['peso_final_kg'] = pedido.peso_cobrar
        
        if pedido.largo_cm and pedido.ancho_cm and pedido.alto_cm:
            validated_data['dimensiones'] = f'{pedido.largo_cm}x{pedido.ancho_cm}x{pedido.alto_cm}'
        
        validated_data['es_fragil'] = pedido.es_fragil
        validated_data['requiere_firma'] = pedido.requiere_firma
        
        # ✅ Usuario que genera la guía
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['generada_por'] = request.user
        
        return super().create(validated_data)


class GuiaEnvioSerializer(serializers.ModelSerializer):
    """Serializer completo para guía"""
    
    pedido = serializers.StringRelatedField(read_only=True)
    numero_guia = serializers.ReadOnlyField()
    codigo_barras = serializers.ReadOnlyField()
    generada_por = serializers.StringRelatedField(read_only=True)
    eventos_tracking = serializers.SerializerMethodField()
    
    class Meta:
        model = GuiaEnvio
        fields = '__all__'
        read_only_fields = [
            'numero_guia', 'codigo_barras', 'codigo_qr',
            'fecha_generacion', 'creado_en', 'actualizado_en'
        ]
    
    def get_eventos_tracking(self, obj):
        from .tracking import EventoTrackingSerializer
        eventos = obj.eventos_tracking.all().order_by('-fecha_registro')[:10]
        return EventoTrackingSerializer(eventos, many=True).data
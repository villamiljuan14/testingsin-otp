from rest_framework import serializers
from ..models import EventoTracking, Pedido


class EventoTrackingSerializer(serializers.ModelSerializer):
    """Serializer de lectura para eventos de tracking"""

    tipo_evento_display = serializers.CharField(
        source='get_tipo_evento_display',
        read_only=True
    )
    hub = serializers.StringRelatedField(read_only=True)
    registrado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventoTracking
        fields = [
            'id', 'tipo_evento', 'tipo_evento_display',
            'ubicacion_texto', 'hub', 'latitud', 'longitud',
            'descripcion', 'observaciones', 'registrado_por',
            'fecha_registro', 'evidencia_foto'
        ]
        read_only_fields = fields


class EventoTrackingCreateSerializer(serializers.ModelSerializer):
    """Serializer de escritura — usado por la app Flutter del mensajero.

    Campos requeridos: pedido, tipo_evento, ubicacion_texto
    Campos opcionales: latitud, longitud, descripcion, observaciones, guia
    El campo registrado_por se asigna en la vista desde request.user.
    """

    class Meta:
        model = EventoTracking
        fields = [
            'pedido', 'guia', 'tipo_evento',
            'ubicacion_texto', 'latitud', 'longitud',
            'descripcion', 'observaciones',
        ]
        extra_kwargs = {
            'guia':             {'required': False, 'allow_null': True},
            'latitud':          {'required': False, 'allow_null': True},
            'longitud':         {'required': False, 'allow_null': True},
            'descripcion':      {'required': False, 'allow_blank': True},
            'observaciones':    {'required': False, 'allow_blank': True},
            'ubicacion_texto':  {'required': False, 'allow_blank': True,
                                 'default': ''},
        }


class TrackingPublicoSerializer(serializers.ModelSerializer):
    """Serializer para tracking público (sin datos sensibles)"""
    
    estado_pedido = serializers.CharField(
        source='pedido.estado',
        read_only=True
    )
    estado_pedido_display = serializers.CharField(
        source='pedido.get_estado_display',
        read_only=True
    )
    ciudad_origen = serializers.CharField(
        source='pedido.ciudad_origen',
        read_only=True
    )
    ciudad_destino = serializers.CharField(
        source='pedido.ciudad_destino',
        read_only=True
    )
    eventos = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'codigo_rastreo', 'numero_pedido',
            'estado_pedido', 'estado_pedido_display',
            'ciudad_origen', 'ciudad_destino',
            'fecha_pedido', 'fecha_estimada_entrega',
            'fecha_entrega_real', 'eventos'
        ]
    
    def get_eventos(self, obj):
        eventos = obj.eventos_tracking.all().order_by('-fecha_registro')[:20]
        return EventoTrackingSerializer(eventos, many=True).data
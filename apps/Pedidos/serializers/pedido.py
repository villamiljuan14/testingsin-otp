from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Pedido, TipoServicio, Hub
from ..services.calculo_tarifas import CalculadoraTarifas

Usuario = get_user_model()


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pedidos"""
    
    tipo_servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoServicio.objects.filter(es_activo=True),
        source='tipo_servicio',
        write_only=True
    )
    
    class Meta:
        model = Pedido
        fields = [
            # Direcciones
            'direccion_origen_texto', 'direccion_destino_texto',
            'ciudad_origen', 'ciudad_destino',
            'departamento_origen', 'departamento_destino',
            'pais_origen', 'pais_destino',
            
            # Destinatario
            'nombre_destinatario', 'telefono_destinatario', 'email_destinatario',
            
            # Servicio
            'tipo_servicio_id',
            
            # Dimensiones y peso
            'peso_real_kg', 'largo_cm', 'ancho_cm', 'alto_cm',
            
            # Contenido
            'descripcion_contenido', 'valor_declarado', 'es_fragil', 'requiere_firma',
            
            # Instrucciones
            'instrucciones_entrega',
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        # ✅ Validar peso
        if data.get('peso_real_kg', 0) <= 0:
            raise serializers.ValidationError({'peso_real_kg': 'El peso debe ser mayor a 0'})
        
        # ✅ Validar dimensiones si existen
        if data.get('largo_cm') and data.get('ancho_cm') and data.get('alto_cm'):
            servicio = data.get('tipo_servicio')
            if servicio:
                if (servicio.largo_max_cm and data['largo_cm'] > servicio.largo_max_cm):
                    raise serializers.ValidationError({
                        'largo_cm': f'Excede el máximo de {servicio.largo_max_cm}cm'
                    })
        
        # ✅ Validar teléfonos
        if data.get('telefono_destinatario'):
            if len(data['telefono_destinatario']) < 7:
                raise serializers.ValidationError({
                    'telefono_destinatario': 'Teléfono inválido'
                })
        
        return data
    
    def create(self, validated_data):
        """Crea el pedido y calcula tarifas automáticamente"""
        request = self.context.get('request')
        
        # ✅ Asignar usuario actual
        validated_data['usuario'] = request.user
        
        # ✅ Calcular tarifas
        pedido_temp = Pedido(**validated_data)
        tarifas = CalculadoraTarifas.calcular(pedido_temp)
        
        validated_data.update(tarifas)
        
        # ✅ Calcular fecha estimada
        pedido_temp.calcular_fecha_estimada()
        validated_data['fecha_estimada_entrega'] = pedido_temp.fecha_estimada_entrega
        
        # ✅ Estado inicial
        validated_data['estado'] = 'BORRADOR'
        
        return super().create(validated_data)


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer completo para lectura de pedidos"""
    
    usuario = serializers.StringRelatedField(read_only=True)
    tipo_servicio = serializers.StringRelatedField(read_only=True)
    hub_origen = serializers.StringRelatedField(read_only=True)
    hub_destino = serializers.StringRelatedField(read_only=True)
    mensajero = serializers.StringRelatedField(read_only=True)
    
    # ✅ Campos calculados
    peso_cobrar = serializers.ReadOnlyField()
    esta_entregado = serializers.ReadOnlyField()
    esta_en_transito = serializers.ReadOnlyField()
    
    # ✅ Relaciones anidadas
    guia = serializers.SerializerMethodField()
    eventos_tracking = serializers.SerializerMethodField()
    prueba_entrega = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = [
            'numero_pedido', 'codigo_rastreo', 'peso_volumetrico_kg',
            'subtotal', 'impuestos', 'descuento', 'total_final',
            'fecha_pedido', 'creado_en', 'actualizado_en'
        ]
    
    def get_guia(self, obj):
        if hasattr(obj, 'guia'):
            return {
                'numero_guia': obj.guia.numero_guia,
                'codigo_barras': obj.guia.codigo_barras,
                'estado': obj.guia.estado,
            }
        return None
    
    def get_eventos_tracking(self, obj):
        from .tracking import EventoTrackingSerializer
        eventos = obj.eventos_tracking.all()[:10]  # Últimos 10 eventos
        return EventoTrackingSerializer(eventos, many=True).data
    
    def get_prueba_entrega(self, obj):
        if hasattr(obj, 'prueba_entrega'):
            return {
                'nombre_recibidor': obj.prueba_entrega.nombre_recibidor,
                'fecha_entrega': obj.prueba_entrega.fecha_entrega,
                'es_validada': obj.prueba_entrega.es_validada,
            }
        return None


class PedidoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar pedidos (solo ciertos campos)"""
    
    class Meta:
        model = Pedido
        fields = [
            'instrucciones_entrega',
            'notas_internas',
            'estado',
            'mensajero',
        ]
    
    def validate_estado(self, value):
        """Validar transiciones de estado"""
        estado_actual = self.instance.estado if self.instance else None
        
        # ✅ Transiciones permitidas
        transiciones = {
            'BORRADOR': ['CONFIRMADO', 'CANCELADO'],
            'CONFIRMADO': ['EN_PREPARACION', 'CANCELADO'],
            'EN_PREPARACION': ['RECOLECTADO'],
            'RECOLECTADO': ['EN_HUB_ORIGEN'],
            'EN_HUB_ORIGEN': ['EN_TRANSITO'],
            'EN_TRANSITO': ['EN_HUB_DESTINO'],
            'EN_HUB_DESTINO': ['EN_REPARTO'],
            'EN_REPARTO': ['ENTREGADO', 'INTENTO_FALLIDO'],
            'INTENTO_FALLIDO': ['EN_REPARTO', 'DEVUELTO'],
        }
        
        if estado_actual and value not in transiciones.get(estado_actual, []):
            raise serializers.ValidationError(
                f'No se puede cambiar de {estado_actual} a {value}'
            )
        
        return value
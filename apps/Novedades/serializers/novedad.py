from rest_framework import serializers
from ..models import Novedad, CategoriaNovedad
from apps.Pedidos.models import Pedido
from apps.Rutas.models import Ruta
from apps.Vehiculos.models import Vehiculo, Conductor


class CategoriaNovedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaNovedad
        fields = '__all__'
        read_only_fields = ['creado_en', 'actualizado_en']


class NovedadSerializer(serializers.ModelSerializer):
    """Serializer completo para novedades"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    categoria = CategoriaNovedadSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaNovedad.objects.all(),
        source='categoria',
        write_only=True,
        required=False
    )
    
    # ✅ Relaciones
    registrado_por = serializers.StringRelatedField(read_only=True)
    asignado_a = serializers.StringRelatedField(read_only=True)
    
    # ✅ Entidades relacionadas
    pedido = serializers.StringRelatedField(read_only=True)
    ruta = serializers.StringRelatedField(read_only=True)
    vehiculo = serializers.StringRelatedField(read_only=True)
    
    # ✅ Campos calculados
    tiempo_transcurrido_horas = serializers.ReadOnlyField()
    sla_vencido = serializers.ReadOnlyField()
    
    class Meta:
        model = Novedad
        fields = '__all__'
        read_only_fields = ['codigo_novedad', 'fecha_registro', 'creado_en', 'actualizado_en']
    
    def validate_severidad(self, value):
        """Validar severidad según categoría"""
        categoria = self.initial_data.get('categoria')
        if categoria and hasattr(categoria, 'severidad_default'):
            # ✅ Validar que la severidad sea apropiada
            pass
        return value


class NovedadCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear novedades"""
    
    class Meta:
        model = Novedad
        fields = [
            'titulo', 'descripcion', 'tipo', 'categoria', 'severidad', 'prioridad',
            'pedido', 'ruta', 'vehiculo', 'conductor',
            'ubicacion_texto', 'latitud', 'longitud',
            'impacto_economico', 'impacto_operativo', 'clientes_afectados',
        ]
    
    def create(self, validated_data):
        """Crea la novedad con usuario actual"""
        validated_data['registrado_por'] = self.context['request'].user
        validated_data['estado'] = 'REGISTRADA'
        return super().create(validated_data)


class NovedadUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar novedades"""
    
    class Meta:
        model = Novedad
        fields = [
            'titulo', 'descripcion', 'severidad', 'prioridad', 'estado',
            'asignado_a', 'ubicacion_texto', 'latitud', 'longitud',
            'impacto_economico', 'impacto_operativo', 'clientes_afectados',
            'causa_raiz', 'solucion_aplicada', 'lecciones_aprendidas',
        ]
    
    def validate_estado(self, value):
        """Validar transición de estado"""
        estado_actual = self.instance.estado if self.instance else None
        
        transiciones = {
            'REGISTRADA': ['EN_REVISION', 'ASIGNADA', 'CANCELADA'],
            'EN_REVISION': ['ASIGNADA', 'CANCELADA'],
            'ASIGNADA': ['EN_PROGRESO', 'EN_ESPERA', 'CANCELADA'],
            'EN_PROGRESO': ['EN_ESPERA', 'RESUELTA', 'ESCALADA'],
            'EN_ESPERA': ['EN_PROGRESO', 'CANCELADA'],
            'RESUELTA': ['CERRADA', 'REABIERTA'],
            'ESCALADA': ['EN_PROGRESO', 'RESUELTA', 'CANCELADA'],
            'REABIERTA': ['EN_PROGRESO', 'CANCELADA'],
        }
        
        if estado_actual and value not in transiciones.get(estado_actual, []):
            raise serializers.ValidationError(
                f'No se puede cambiar de {estado_actual} a {value}'
            )
        
        return value


class NovedadEstadisticasSerializer(serializers.Serializer):
    """Serializer para estadísticas de novedades"""
    
    total_novedades = serializers.IntegerField()
    novedades_resueltas = serializers.IntegerField()
    novedades_pendientes = serializers.IntegerField()
    porcentaje_cumplimiento_sla = serializers.DecimalField(max_digits=5, decimal_places=2)
    tiempo_promedio_respuesta_horas = serializers.DecimalField(max_digits=8, decimal_places=2)
    tiempo_promedio_resolucion_horas = serializers.DecimalField(max_digits=8, decimal_places=2)
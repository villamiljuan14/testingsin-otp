from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone  
from ..models import Pedido, GuiaEnvio, TipoServicio
from ..serializers.pedido import (
    PedidoSerializer, PedidoCreateSerializer, PedidoUpdateSerializer
)
from ..serializers.guia import GuiaCreateSerializer, GuiaEnvioSerializer
from ..permissions import IsAdminUser, IsMensajero, IsCliente, IsOwnerOrAdmin


class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pedidos"""
    
    queryset = Pedido.objects.select_related(
        'usuario', 'tipo_servicio', 'hub_origen', 'hub_destino', 'mensajero'
    ).prefetch_related('eventos_tracking', 'reclamos')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PedidoUpdateSerializer
        return PedidoSerializer
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        elif self.action == 'assign_mensajero':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtrar pedidos según el rol del usuario"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.es_admin():
            return queryset  
        
        if user.es_mensajero():
            return queryset.filter(mensajero=user) 
        
        return queryset.filter(usuario=user) 
    
    def perform_create(self, serializer):
        """Acciones después de crear pedido"""
        pedido = serializer.save()
        
        # ✅ Crear evento de tracking inicial
        from ..models import EventoTracking, TipoEventoTracking
        EventoTracking.objects.create(
            pedido=pedido,
            tipo_evento=TipoEventoTracking.GUIA_CREADA,
            ubicacion_texto=f'{pedido.ciudad_origen}, {pedido.departamento_origen}',
            registrado_por=self.request.user,
            descripcion='Pedido creado en el sistema'
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_mensajero(self, request, pk=None):
        """Asignar mensajero al pedido"""
        pedido = self.get_object()
        mensajero_id = request.data.get('mensajero_id')
        
        if not mensajero_id:
            return Response(
                {'error': 'mensajero_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        
        try:
            mensajero = Usuario.objects.get(
                id=mensajero_id,
                rol__tipo_rol='MENSAJERO'
            )
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Mensajero no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        pedido.mensajero = mensajero
        pedido.save()
        
        # ✅ Crear evento de tracking
        from ..models import EventoTracking, TipoEventoTracking
        EventoTracking.objects.create(
            pedido=pedido,
            tipo_evento=TipoEventoTracking.EN_REPARTO,
            ubicacion_texto=f'Asignado a {mensajero.nombre_completo}',
            registrado_por=request.user,
            descripcion=f'Mensajero {mensajero.email} asignado'
        )
        
        return Response({
            'message': 'Mensajero asignado exitosamente',
            'mensajero': mensajero.email
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def cancelar(self, request, pk=None):
        """Cancelar pedido"""
        pedido = self.get_object()
        
        if not pedido.puede_cancelar(request.user):
            return Response(
                {'error': 'No se puede cancelar este pedido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.estado = 'CANCELADO'
        pedido.save()
        
        # ✅ Crear evento de tracking
        from ..models import EventoTracking, TipoEventoTracking
        EventoTracking.objects.create(
            pedido=pedido,
            tipo_evento=TipoEventoTracking.CANCELADO,
            ubicacion_texto=pedido.ciudad_origen,
            registrado_por=request.user,
            descripcion='Pedido cancelado por el usuario'
        )
        
        return Response({'message': 'Pedido cancelado exitosamente'})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_pedidos(self, request):
        """Obtener pedidos del usuario actual"""
        queryset = self.get_queryset().filter(usuario=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GenerarGuiaView(generics.GenericAPIView):
    """Generar guía de envío para un pedido"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        
        # Lógica para generar guía
        from ..models.guia import GuiaEnvio
        from ..serializers.guia import GuiaCreateSerializer
        
        guia_data = {
            'pedido': pedido.id,
            'numero_guia': f'GUIA-{pedido.numero_pedido}',
            'instrucciones_especiales': request.data.get('instrucciones_especiales', ''),
        }
        
        serializer = GuiaCreateSerializer(data=guia_data)
        if serializer.is_valid():
            guia = serializer.save()
            return Response(GuiaCreateSerializer(guia).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrarEntregaView(generics.GenericAPIView):
    """Registrar entrega de un pedido"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        
        # Cambiar estado a entregado
        from ..models.choices import EstadoPedido
        pedido.estado = EstadoPedido.ENTREGADO
        pedido.fecha_entrega_real = timezone.now()
        pedido.save()
        
        return Response({'message': 'Entrega registrada exitosamente'})
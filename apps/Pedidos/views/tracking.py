from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from ..models import EventoTracking, Pedido
from ..serializers.tracking import EventoTrackingSerializer, EventoTrackingCreateSerializer, TrackingPublicoSerializer
from ..permissions import IsAdminUser, IsMensajero


class TrackingViewSet(viewsets.ModelViewSet):
    """ViewSet para eventos de tracking"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return EventoTrackingCreateSerializer
        return EventoTrackingSerializer

    def get_queryset(self):
        user = self.request.user

        if user.es_admin():
            return EventoTracking.objects.select_related(
                'pedido', 'hub', 'registrado_por'
            )

        if user.es_mensajero():
            return EventoTracking.objects.filter(
                pedido__mensajero=user
            ).select_related('pedido', 'hub', 'registrado_por')

        return EventoTracking.objects.filter(
            pedido__usuario=user
        ).select_related('pedido', 'hub', 'registrado_por')

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)


class TrackingPublicoView(generics.RetrieveAPIView):
    """
    Vista pública para tracking sin autenticación.
    Similar a fedex.com/tracking
    """
    serializer_class = TrackingPublicoSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'codigo_rastreo'
    
    def get_queryset(self):
        return Pedido.objects.select_related(
            'tipo_servicio', 'hub_origen', 'hub_destino'
        ).prefetch_related('eventos_tracking')
    
    def retrieve(self, request, *args, **kwargs):
        codigo = kwargs.get('codigo_rastreo')
        
        try:
            pedido = Pedido.objects.get(codigo_rastreo=codigo)
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Código de rastreo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)
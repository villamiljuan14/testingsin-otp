from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Reclamo
from ..serializers.reclamo import ReclamoSerializer, ReclamoCreateSerializer
from ..permissions import IsAdminUser, IsOwnerOrAdmin


class ReclamoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de reclamos"""
    
    serializer_class = ReclamoSerializer
    permission_classes = [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReclamoCreateSerializer
        return ReclamoSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.es_admin():
            return Reclamo.objects.select_related('pedido', 'reclamante', 'asignado_a')
        
        return Reclamo.objects.filter(
            reclamante=user
        ).select_related('pedido', 'reclamante', 'asignado_a')
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def aprobar(self, request, pk=None):
        """Aprobar reclamo"""
        reclamo = self.get_object()
        valor = request.data.get('valor_aprobado')
        
        if not valor:
            return Response(
                {'error': 'valor_aprobado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reclamo.aprobar(valor, request.user)
        
        return Response({
            'message': 'Reclamo aprobado',
            'valor_aprobado': valor
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def rechazar(self, request, pk=None):
        """Rechazar reclamo"""
        reclamo = self.get_object()
        motivo = request.data.get('motivo')
        
        if not motivo:
            return Response(
                {'error': 'motivo es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reclamo.rechazar(motivo, request.user)
        
        return Response({'message': 'Reclamo rechazado'})
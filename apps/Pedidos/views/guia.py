from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import GuiaEnvio
from ..serializers.guia import GuiaEnvioSerializer, GuiaCreateSerializer
from ..permissions import IsAdminUser


class GuiaEnvioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de guías"""
    
    serializer_class = GuiaEnvioSerializer
    permission_classes = [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GuiaCreateSerializer
        return GuiaEnvioSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.es_admin():
            return GuiaEnvio.objects.select_related('pedido', 'generada_por')
        
        return GuiaEnvio.objects.filter(
            pedido__usuario=user
        ).select_related('pedido', 'generada_por')


class GenerarGuiaView(generics.CreateAPIView):
    """Vista específica para generar guía de un pedido"""
    
    serializer_class = GuiaCreateSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guia = serializer.save()
        
        return Response(
            GuiaEnvioSerializer(guia).data,
            status=status.HTTP_201_CREATED
        )
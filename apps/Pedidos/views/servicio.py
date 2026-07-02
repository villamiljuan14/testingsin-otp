from rest_framework import viewsets, permissions
from ..models import TipoServicio
from ..serializers.servicio import TipoServicioSerializer


class TipoServicioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de servicio (lectura pública)"""
    
    queryset = TipoServicio.objects.filter(es_activo=True)
    serializer_class = TipoServicioSerializer
    permission_classes = [permissions.AllowAny]
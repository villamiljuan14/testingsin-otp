from rest_framework import viewsets, permissions
from ..models import Hub
from ..serializers.hub import HubSerializer
from ..permissions import IsAdminUser


class HubViewSet(viewsets.ModelViewSet):
    """ViewSet para hubs (solo admin)"""
    
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    permission_classes = [IsAdminUser]
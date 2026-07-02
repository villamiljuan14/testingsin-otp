from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from .models import Pais, Departamento, Ciudad, Hub
from .serializers import PaisSerializer, DepartamentoSerializer, CiudadSerializer, HubSerializer


class PaisViewSet(viewsets.ReadOnlyModelViewSet):
    """API pública para listar países"""
    queryset = Pais.objects.filter(es_activo=True)
    serializer_class = PaisSerializer
    permission_classes = [permissions.AllowAny]


class DepartamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """API para departamentos filtrados por país"""
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        pais_id = self.request.query_params.get('pais_id')
        queryset = Departamento.objects.filter(es_activo=True)
        
        if pais_id:
            queryset = queryset.filter(pais_id=pais_id)
        
        return queryset.select_related('pais')


class CiudadViewSet(viewsets.ReadOnlyModelViewSet):
    """API para ciudades filtradas por departamento"""
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        departamento_id = self.request.query_params.get('departamento_id')
        queryset = Ciudad.objects.filter(es_activo=True)
        
        if departamento_id:
            queryset = queryset.filter(departamento_id=departamento_id)
        
        return queryset.select_related('departamento__pais')


class HubViewSet(viewsets.ModelViewSet):
    """API para gestión de hubs"""
    queryset = Hub.objects.filter(es_activo=True)
    serializer_class = HubSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ciudad_id = self.request.GET.get('ciudad_id')
        tipo_hub = self.request.GET.get('tipo_hub')
        
        if ciudad_id:
            queryset = queryset.filter(ciudad_id=ciudad_id)
        if tipo_hub:
            queryset = queryset.filter(tipo_hub=tipo_hub)
            
        return queryset.select_related('ciudad__departamento__pais')
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar hub"""
        hub = get_object_or_404(Hub, pk=pk)
        hub.es_activo = True
        hub.save()
        return Response({'status': 'hub activado'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar hub"""
        hub = get_object_or_404(Hub, pk=pk)
        hub.es_activo = False
        hub.save()
        return Response({'status': 'hub desactivado'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ubicaciones_en_cascada(request):
    """
    Endpoint para selectores en cascada (País → Departamento → Ciudad).
    Ideal para frontend con dropdowns dependientes.
    """
    pais_id = request.query_params.get('pais_id')
    departamento_id = request.query_params.get('departamento_id')
    
    response = {
        'paises': PaisSerializer(Pais.objects.filter(es_activo=True), many=True).data,
        'departamentos': [],
        'ciudades': [],
    }
    
    if pais_id:
        response['departamentos'] = DepartamentoSerializer(
            Departamento.objects.filter(pais_id=pais_id, es_activo=True),
            many=True
        ).data
    
    if departamento_id:
        response['ciudades'] = CiudadSerializer(
            Ciudad.objects.filter(departamento_id=departamento_id, es_activo=True),
            many=True
        ).data
    
    return Response(response)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def buscar_ciudades(request):
    """Búsqueda de ciudades por nombre (autocomplete)"""
    query = request.query_params.get('q', '')
    
    if len(query) < 3:
        return Response({'error': 'Mínimo 3 caracteres'}, status=400)
    
    ciudades = Ciudad.objects.filter(
        nombre__icontains=query,
        es_activo=True
    ).select_related('departamento__pais')[:20]
    
    serializer = CiudadSerializer(ciudades, many=True)
    return Response(serializer.data)
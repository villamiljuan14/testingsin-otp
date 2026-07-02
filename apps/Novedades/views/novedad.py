from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Novedad, EvidenciaNovedad, AccionCorrectiva
from ..serializers.novedad import (
    NovedadSerializer,
    NovedadCreateSerializer,
    NovedadUpdateSerializer,
    NovedadEstadisticasSerializer,
)
from ..serializers.evidencia import EvidenciaNovedadSerializer
from ..serializers.accion import AccionCorrectivaSerializer
from ..permissions import IsAdminUser, IsNovedadesManager


class NovedadViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de novedades"""
    
    queryset = Novedad.objects.select_related(
        'categoria', 'registrado_por', 'asignado_a',
        'pedido', 'ruta', 'vehiculo'
    ).prefetch_related(
        'evidencias', 'acciones_correctivas', 'seguimientos'
    ).all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NovedadCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NovedadUpdateSerializer
        return NovedadSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser() | IsNovedadesManager()]
        elif self.action in ['asignar', 'escalar', 'resolver', 'cerrar']:
            return [IsAdminUser() | IsNovedadesManager()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.es_admin():
            return super().get_queryset()
        
        # Usuarios ven solo sus novedades
        return Novedad.objects.filter(
            models.Q(registrado_por=user) |
            models.Q(asignado_a=user)
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser() | IsNovedadesManager()])
    def asignar(self, request, pk=None):
        """Asignar novedad a usuario"""
        novedad = self.get_object()
        usuario_id = request.data.get('usuario_id')
        
        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        novedad.asignar(usuario_asignado=usuario, usuario_asigna=request.user)
        
        return Response({
            'message': 'Novedad asignada',
            'asignado_a': usuario.email
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser() | IsNovedadesManager()])
    def escalar(self, request, pk=None):
        """Escalar novedad"""
        novedad = self.get_object()
        usuario_id = request.data.get('usuario_id')
        motivo = request.data.get('motivo')
        
        if not usuario_id or not motivo:
            return Response(
                {'error': 'usuario_id y motivo son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        novedad.escalar(usuario_destino=usuario, motivo=motivo, usuario_escala=request.user)
        
        return Response({
            'message': 'Novedad escalada',
            'nivel': novedad.nivel_escalamiento
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated()])
    def resolver(self, request, pk=None):
        """Resolver novedad"""
        novedad = self.get_object()
        solucion = request.data.get('solucion')
        causa_raiz = request.data.get('causa_raiz')
        
        if not novedad.puede_resolver(request.user):
            return Response(
                {'error': 'No tienes permisos para resolver esta novedad'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        novedad.causa_raiz = causa_raiz
        novedad.solucion_aplicada = solucion
        novedad.actualizar_estado('RESUELTA', request.user)
        
        return Response({
            'message': 'Novedad resuelta',
            'fecha_resolucion': novedad.fecha_resolucion
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser() | IsNovedadesManager()])
    def cerrar(self, request, pk=None):
        """Cerrar novedad"""
        novedad = self.get_object()
        
        if novedad.estado != 'RESUELTA':
            return Response(
                {'error': 'La novedad debe estar RESUELTA para cerrar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        novedad.actualizar_estado('CERRADA', request.user)
        
        return Response({'message': 'Novedad cerrada'})
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated()])
    def evidencias(self, request, pk=None):
        """Obtener evidencias de la novedad"""
        novedad = self.get_object()
        evidencias = novedad.evidencias.all()
        serializer = EvidenciaNovedadSerializer(evidencias, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated()])
    def acciones(self, request, pk=None):
        """Obtener acciones correctivas de la novedad"""
        novedad = self.get_object()
        acciones = novedad.acciones_correctivas.all()
        serializer = AccionCorrectivaSerializer(acciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser() | IsNovedadesManager()])
    def estadisticas(self, request):
        """Obtener estadísticas de novedades"""
        from django.db.models import Count, Avg, Sum, Q
        from datetime import timedelta
        
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = self.get_queryset()
        
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha_registro__range=[fecha_inicio, fecha_fin])
        
        total = queryset.count()
        resueltas = queryset.filter(estado='RESUELTA').count()
        pendientes = queryset.filter(estado__in=['REGISTRADA', 'EN_REVISION', 'ASIGNADA', 'EN_PROGRESO']).count()
        
        sla_cumplido = queryset.filter(sla_cumplido=True).count()
        porcentaje_sla = round((sla_cumplido / total * 100) if total > 0 else 0, 2)
        
        avg_respuesta = queryset.filter(
            tiempo_respuesta_horas__isnull=False
        ).aggregate(Avg('tiempo_respuesta_horas'))['tiempo_respuesta_horas__avg'] or 0
        
        avg_resolucion = queryset.filter(
            tiempo_resolucion_horas__isnull=False
        ).aggregate(Avg('tiempo_resolucion_horas'))['tiempo_resolucion_horas__avg'] or 0
        
        return Response({
            'total_novedades': total,
            'novedades_resueltas': resueltas,
            'novedades_pendientes': pendientes,
            'porcentaje_cumplimiento_sla': porcentaje_sla,
            'tiempo_promedio_respuesta_horas': round(avg_respuesta, 2),
            'tiempo_promedio_resolucion_horas': round(avg_resolucion, 2),
        })
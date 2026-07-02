"""
Class-Based Views (CBV) for Usuario Management - Modern Django Pattern

ADVANTAGES OVER FBV:
- ✓ Code reuse through inheritance and mixins
- ✓ Better structure for complex views
- ✓ Built-in HTTP method handling (GET, POST, etc.)
- ✓ Easier to test and maintain
- ✓ Automatic login_required via decorators
- ✓ Permission handling via mixins

This module provides modern CBV implementations as an alternative
to function-based views (FBV).
"""

import logging
from typing import Optional, Dict, Any

from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import QuerySet, Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from apps.Autenticacion.models import Usuario, Rol, TipoRol
from apps.Autenticacion.services import (
    UsuarioService,
    UsuarioExportService,
    UsuarioValidationService,
)
from apps.Autenticacion.services.pagination import PaginationService
from apps.core.decorators import role_required

logger = logging.getLogger(__name__)


# ── CUSTOM MIXINS ──

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin que requiere que el usuario sea administrador."""
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar que el usuario sea admin antes de procesar."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar si es admin
        if not (hasattr(request.user, 'rol') and request.user.rol.tipo_rol == TipoRol.ADMINISTRADOR):
            raise PermissionError('No tienes permisos para acceder a esta vista.')
        
        return super().dispatch(request, *args, **kwargs)


class OptimizedQuerysetMixin:
    """Mixin que aplica optimizaciones automáticas al queryset."""
    
    def get_queryset(self) -> QuerySet:
        """Retorna un queryset optimizado con select_related."""
        queryset = super().get_queryset()
        # Aplicar select_related para evitar N+1 queries
        return queryset.select_related('rol').order_by('-fecha_creacion')


class FilteringMixin:
    """Mixin que proporciona funcionalidad de filtrado y búsqueda."""
    
    def get_search_query(self) -> str:
        """Obtener y limpiar el query de búsqueda."""
        return self.request.GET.get('q', '').strip()
    
    def get_role_filter(self) -> Optional[int]:
        """Obtener y validar el filtro de rol."""
        rol_id = self.request.GET.get('rol', '').strip()
        if rol_id and rol_id.isdigit():
            try:
                return int(rol_id)
            except ValueError:
                logger.warning(f'Invalid rol filter: {rol_id}')
        return None
    
    def get_status_filter(self) -> Optional[bool]:
        """Obtener y validar el filtro de estado."""
        status = self.request.GET.get('status', '').strip().lower()
        if status == 'activo':
            return True
        elif status == 'inactivo':
            return False
        return None
    
    def apply_filters(self, queryset: QuerySet) -> QuerySet:
        """Aplicar todos los filtros al queryset."""
        # Búsqueda
        search_query = self.get_search_query()
        if search_query:
            queryset = queryset.filter(
                Q(primer_nombre__icontains=search_query) |
                Q(segundo_nombre__icontains=search_query) |
                Q(apellido_paterno__icontains=search_query) |
                Q(apellido_materno__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(doc_usuario__icontains=search_query) |
                Q(telefono__icontains=search_query)
            )
        
        # Filtro de rol
        rol_id = self.get_role_filter()
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)
        
        # Filtro de estado
        status = self.get_status_filter()
        if status is not None:
            queryset = queryset.filter(estado_usuario=status)
        
        return queryset


class PaginationMixin:
    """Mixin que proporciona funcionalidad de paginación optimizada."""
    
    paginate_by = 15  # Default items per page
    
    def get_paginate_by(self, queryset: QuerySet) -> int:
        """Obtener items por página del request, validado."""
        per_page = self.request.GET.get('per_page', self.paginate_by)
        return PaginationService.validate_per_page(per_page)
    
    def paginate_queryset(self, queryset: QuerySet, page_size: int) -> tuple:
        """Usar PaginationService en lugar de paginator por defecto."""
        page = self.request.GET.get('page', 1)
        page_obj, pagination_info = PaginationService.paginate(
            queryset,
            page=page,
            per_page=page_size,
            count_total=True
        )
        return page_obj, pagination_info


class CachedStatisticssMixin:
    """Mixin que proporciona estadísticas en caché."""
    
    STATS_CACHE_KEY = 'usuario_stats_dashboard'
    STATS_CACHE_TIMEOUT = 300  # 5 minutos
    
    def get_stats(self) -> Dict[str, int]:
        """Obtener estadísticas (del caché si está disponible)."""
        stats = cache.get(self.STATS_CACHE_KEY)
        
        if stats is None:
            logger.debug('Stats cache miss, running aggregate query')
            stats = UsuarioService.get_usuario_stats()
            cache.set(self.STATS_CACHE_KEY, stats, self.STATS_CACHE_TIMEOUT)
            logger.info('Stats cached for 5 minutes')
        else:
            logger.debug('Stats retrieved from cache')
        
        return stats
    
    def invalidate_stats_cache(self):
        """Invalidar la caché de estadísticas (ej: después de crear/actualizar/eliminar usuario)."""
        cache.delete(self.STATS_CACHE_KEY)
        logger.info('Stats cache invalidated')


# ── CLASS-BASED VIEWS ──

class UsuarioListView(
    AdminRequiredMixin,
    OptimizedQuerysetMixin,
    FilteringMixin,
    PaginationMixin,
    CachedStatisticssMixin,
    ListView
):
    """
    📊 Optimized Class-Based View for Usuario Listing
    
    FEATURES:
    - Mixins for code organization and reuse
    - Automatic queryset optimization (select_related)
    - Built-in filtering and search
    - Paginated results with validation
    - Cached statistics
    - Admin-only access
    
    MIXINS STACKED:
    1. AdminRequiredMixin: Requiere admin
    2. OptimizedQuerysetMixin: select_related('rol')
    3. FilteringMixin: Búsqueda, rol, estado
    4. PaginationMixin: Paginación con validación
    5. CachedStatisticssMixin: Stats en caché
    6. ListView: Django's built-in generic list view
    
    Inheritance Order: Left-to-right, Django calls MRO (Method Resolution Order)
    """
    
    model = Usuario
    template_name = 'dashboard/usuarios_cbv.html'
    context_object_name = 'usuarios'
    paginate_by = 15
    
    def get_queryset(self) -> QuerySet:
        """
        Build optimized queryset with all filters applied.
        
        Chain:
        1. OptimizedQuerysetMixin.get_queryset() - select_related + order
        2. FilteringMixin.apply_filters() - search, role, status
        3. Return filtered & optimized queryset
        """
        queryset = super().get_queryset()
        return self.apply_filters(queryset)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare context with pagination info and statistics.
        
        Adds:
        - pagination_info: Detailed pagination metadata
        - page_range: Smart page range for template
        - url_params: Query params for maintaining filters
        - stats: Cached usuario statistics
        - roles: Available roles for filter dropdown
        - filters: Current filter values for template
        """
        context = super().get_context_data(**kwargs)
        
        # Get pagination info
        page_obj = context['page_obj']
        paginator = page_obj.paginator
        
        # Add detailed pagination info
        context['pagination_info'] = {
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'per_page': self.get_paginate_by(self.get_queryset()),
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
        
        # Smart page range for template
        context['page_range'] = PaginationService.get_page_range_display(
            total_pages=paginator.num_pages,
            current_page=page_obj.number,
            window=2
        )
        
        # URL params for maintaining filters during navigation
        context['url_params'] = PaginationService.build_pagination_url_params(
            query_params=self.request.GET,
            exclude_fields=['page', 'csrftoken']
        )
        
        # Cached statistics
        context['stats'] = self.get_stats()
        
        # Available roles for dropdown
        context['roles'] = Rol.objects.all().order_by('nombre')
        
        # Current filter values for template
        context['search_query'] = self.get_search_query()
        context['selected_rol'] = self.get_role_filter()
        context['selected_status'] = self.get_status_filter()
        
        # Counter shortcuts
        context['active_usuarios_count'] = context['stats']['activos']
        context['inactive_usuarios_count'] = context['stats']['inactivos']
        context['total_usuarios_count'] = context['stats']['total']
        
        logger.info(
            f'UsuarioListView - Page {context["pagination_info"]["current_page"]} '
            f'of {context["pagination_info"]["total_pages"]}, '
            f'Total: {context["pagination_info"]["total_count"]}'
        )
        
        return context


class UsuarioExportView(AdminRequiredMixin, FilteringMixin, FormView):
    """
    📥 Optimized Class-Based View for Usuario Export
    
    Handles export in PDF, XLSX, CSV formats.
    
    MIXINS:
    - AdminRequiredMixin: Admin-only access
    - FilteringMixin: Apply search/role/status filters
    - FormView: Django's default form handler (inherits dispatch for POST/GET)
    """
    
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        """Handle export POST request."""
        
        # Extract parameters
        export_format = request.POST.get('format', 'csv').lower()
        
        logger.info(f'Export request - Format: {export_format}')
        
        # Validate format
        ALLOWED_FORMATS = ['pdf', 'xlsx', 'csv']
        if export_format not in ALLOWED_FORMATS:
            logger.warning(f'Invalid export format: {export_format}')
            return JsonResponse(
                {'error': f'Format no permitido. Intenta con: {", ".join(ALLOWED_FORMATS)}'},
                status=400
            )
        
        # Build queryset with filters
        queryset = Usuario.objects.select_related('rol').order_by('-fecha_creacion')
        queryset = self.apply_filters(queryset)
        
        logger.info(f'Export dataset size: {queryset.count()} usuarios')
        
        # Export
        try:
            response = UsuarioExportService.export(
                queryset,
                file_format=export_format
            )
            return response
        except Exception as e:
            logger.exception(f'Export error: {str(e)}')
            return JsonResponse(
                {'error': f'Error durante la exportación: {str(e)}'},
                status=500
            )

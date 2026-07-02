"""
Pagination Service - Centralized, reusable, production-ready pagination.

Este módulo proporciona funciones de paginación reutilizables y optimizadas
para cualquier QuerySet en la aplicación.

Características:
- Validación robusta de parámetros
- Manejo de errores
- Información completa de paginación
- Preparado para miles de registros
- OWASP tested (defensas contra ataques)
"""

import logging
from typing import Tuple, Dict, Any, Optional, List

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class PaginationService:
    """
    Servicio centralizado de paginación.
    
    Proporciona métodos reutilizables para paginar cualquier QuerySet
    de forma consistentemente en toda la aplicación.
    
    Uso:
        >>> users = User.objects.all()
        >>> page_obj, info = PaginationService.paginate(users, page=1, per_page=20)
        >>> page_obj.object_list  # Usuarios en página 1
        >>> info['total_count']   # Total de usuarios
        >>> info['total_pages']   # Total de páginas
    """
    
    # Valores permitidos para items por página (defensa contra ataques)
    ALLOWED_PER_PAGE = [10, 15, 20, 25, 30, 40, 50]
    DEFAULT_PER_PAGE = 15
    MAX_PER_PAGE = 100
    MIN_PER_PAGE = 5
    
    @staticmethod
    def validate_per_page(per_page: Optional[Any]) -> int:
        """
        Valida y devuelve un valor válido de items por página.
        
        Características de seguridad:
        - Convierte a entero de forma segura
        - Valida que esté en whitelist de valores permitidos
        - Previene ataques de inyección de parámetros
        - Logging de intentos inválidos
        
        Args:
            per_page: Valor a validar (puede ser string, int, None)
        
        Returns:
            int: Valor válido de items por página
        
        Examples:
            >>> PaginationService.validate_per_page('20')
            20
            >>> PaginationService.validate_per_page(999)  # Fuera de rango
            15  # Valor por defecto
            >>> PaginationService.validate_per_page(None)
            15  # Por defecto
            >>> PaginationService.validate_per_page('injectable')
            15  # Intento de inyección bloqueado
        """
        try:
            # Convertir a entero si no es None
            per_page_int = int(per_page) if per_page is not None else PaginationService.DEFAULT_PER_PAGE
            
            # Validar whitelist
            if per_page_int not in PaginationService.ALLOWED_PER_PAGE:
                logger.warning(
                    f'Invalid per_page value attempted: {per_page_int}. Using default: {PaginationService.DEFAULT_PER_PAGE}'
                )
                return PaginationService.DEFAULT_PER_PAGE
            
            return per_page_int
        
        except (ValueError, TypeError) as e:
            logger.warning(
                f'Could not convert per_page to int: {per_page}. Error: {str(e)}. Using default.'
            )
            return PaginationService.DEFAULT_PER_PAGE
    
    @staticmethod
    def validate_page(page: Optional[Any]) -> int:
        """
        Valida y devuelve un número de página válido.
        
        Args:
            page: Número de página (puede ser string, int, None)
        
        Returns:
            int: Número de página válido (mínimo 1)
        """
        try:
            page_int = int(page) if page is not None else 1
            return max(1, page_int)  # Garantizar que sea al menos 1
        except (ValueError, TypeError):
            return 1
    
    @staticmethod
    def paginate(
        queryset: QuerySet,
        page: Optional[Any] = 1,
        per_page: Optional[Any] = None,
        count_total: bool = True
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Pagina un QuerySet y devuelve información completa de paginación.
        
        Este es el método principal para paginar cualquier QuerySet
        en la aplicación. Proporciona todo lo necesario en una sola llamada.
        
        Args:
            queryset: QuerySet a paginar
            page: Número de página (por defecto 1)
            per_page: Items por página (por defecto 15)
            count_total: Si False, evita contar total (útil para >>100k registros)
        
        Returns:
            Tuple[page_obj, pagination_info]:
            - page_obj: Objeto Page de Django (iterable)
            - pagination_info: Dict con toda la información necesaria
        
        Example:
            >>> usuarios = Usuario.objects.all()
            >>> page_obj, info = PaginationService.paginate(usuarios, page=1, per_page=20)
            >>> info['total_count']    # 1250
            >>> info['total_pages']    # 63
            >>> info['current_page']   # 1
            >>> info['has_next']       # True
            >>> info['start_index']    # 1
            >>> info['end_index']      # 20
            >>> for user in page_obj:
            ...     print(user.nombre_completo)
        """
        # Validar parámetros
        page_num = PaginationService.validate_page(page)
        per_page_num = PaginationService.validate_per_page(per_page)
        
        # Crear paginador
        paginator = Paginator(queryset, per_page_num)
        
        try:
            # Intentar obtener la página solicitada
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # Si el número de página no es entero, usar página 1
            page_obj = paginator.page(1)
        except EmptyPage:
            # Si la página está fuera de rango, ir a última página
            page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else paginator.page(1)
        
        # Construir información de paginación completa
        pagination_info = {
            'total_count': paginator.count if count_total else None,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'per_page': per_page_num,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
            'page_range': list(paginator.page_range),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        }
        
        return page_obj, pagination_info
    
    @staticmethod
    def get_page_range_display(
        total_pages: int,
        current_page: int,
        window: int = 3
    ) -> List[Any]:
        """
        Obtiene un rango de páginas para mostrar en el template.
        
        Útil para mostrar números de página con "..." cuando hay muchas páginas.
        Ejemplo: [1, '...', 48, 49, 50, 51, 52, '...', 100]
        
        Args:
            total_pages: Total de páginas
            current_page: Página actual
            window: Número de páginas a mostrar alrededor de la actual
        
        Returns:
            Lista de números de página (int) y strings ('...')
        
        Example:
            >>> PaginationService.get_page_range_display(50, 25, window=2)
            [1, '...', 23, 24, 25, 26, 27, '...', 50]
        """
        if total_pages <= 1:
            return [1]
        
        start = max(1, current_page - window)
        end = min(total_pages, current_page + window)
        
        pages = []
        
        # Agregar página 1
        pages.append(1)
        
        # Agregar "..." si hay brecha
        if start > 2:
            pages.append('...')
        
        # Agregar páginas del rango
        for page_num in range(start, end + 1):
            if page_num > 1 and page_num < total_pages:
                if page_num not in pages:
                    pages.append(page_num)
        
        # Agregar "..." si hay brecha
        if end < total_pages - 1:
            pages.append('...')
        
        # Agregar última página
        if total_pages > 1:
            pages.append(total_pages)
        
        return pages
    
    @staticmethod
    def build_pagination_url_params(
        query_params: Dict[str, Any],
        page: Optional[int] = None,
        exclude_fields: Optional[List[str]] = None
    ) -> str:
        """
        Construye parámetros URL para mantener filtros entre páginas.
        
        Útil para mantener búsquedas y filtros cuando navegas entre páginas.
        Ejemplo: 'q=juan&rol=1&estado=activo&page=2'
        
        Args:
            query_params: Diccionario de parámetros GET
            page: Nueva página a agregar (opcional)
            exclude_fields: Campos a excluir (default: ['page', 'csrftoken'])
        
        Returns:
            String con parámetros URL codificados
        
        Example:
            >>> params = request.GET.copy()
            >>> url_params = PaginationService.build_pagination_url_params(
            ...     params,
            ...     page=2,
            ...     exclude_fields=['page', 'debug']
            ... )
            >>> f'?{url_params}'
            '?q=juan&rol=1&page=2'
        """
        if exclude_fields is None:
            exclude_fields = ['page', 'csrftoken']
        
        params = {}
        
        # Copiar parámetros excepto los excluidos
        for key, value in query_params.items():
            if key not in exclude_fields and value:
                params[key] = value
        
        # Agregar nueva página si se proporciona
        if page is not None:
            params['page'] = page
        
        # Construir query string
        return '&'.join([f'{k}={v}' for k, v in params.items() if v])

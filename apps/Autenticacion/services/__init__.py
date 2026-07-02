"""
Autenticacion Services Module

This package contains all business logic services for usuario (user) management.
Services are organized by concern: CRUD, validation, and export operations.

Example Usage:
    from apps.Autenticacion.services import UsuarioService, UsuarioExportService
    
    # Create a new usuario
    usuario, errors = UsuarioService.create_usuario({
        'email': 'user@example.com',
        'password': 'SecurePass123',
        'primer_nombre': 'Juan',
        'rol_id': 1,
    })
    
    # Filter usuarios
    queryset = UsuarioService.filter_usuarios_queryset(
        search_query='juan',
        rol_id=1
    )
    
    # Export to Excel
    response = UsuarioExportService.export(queryset, file_format='xlsx')
"""

from .base import ServiceBase
from .usuario_service import UsuarioService
from .validation_service import UsuarioValidationService
from .export_service import UsuarioExportService

__all__ = [
    'ServiceBase',
    'UsuarioService',
    'UsuarioValidationService',
    'UsuarioExportService',
]

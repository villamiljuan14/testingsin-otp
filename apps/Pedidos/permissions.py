from apps.core.permissions import (
    BaseRolePermission, IsAdminUser, IsMensajero, IsCliente, 
    IsOwnerOrAdmin, CanCreatePedido
)

# Reexportar para compatibilidad con código existente
__all__ = [
    'BaseRolePermission', 'IsAdminUser', 'IsMensajero', 'IsCliente',
    'IsOwnerOrAdmin', 'CanCreatePedido'
]

from apps.core.permissions import (
    BaseRolePermission, IsAdminUser, IsMensajero, IsCliente,
    IsOwnerOrAdmin, CanManageUsers
)

# Reexportamos absolutamente todo para compatibilidad total del sistema
__all__ = [
    'BaseRolePermission', 
    'IsAdminUser', 
    'IsMensajero', 
    'IsCliente',
    'IsOwnerOrAdmin', 
    'CanManageUsers',
]
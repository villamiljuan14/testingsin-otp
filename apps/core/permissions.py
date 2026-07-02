from rest_framework import permissions
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class BaseRolePermission(permissions.BasePermission):
    """
    Sistema unificado de permisos por rol
    Reemplaza las implementaciones duplicadas en Autenticacion y Pedidos
    """
    
    # Mapeo de permisos por rol
    ROLE_PERMISSIONS = {
        'ADMIN': {
            'create': ['pedido', 'guia', 'hub', 'usuario', 'reclamo'],
            'read': ['pedido', 'guia', 'hub', 'usuario', 'reclamo'],
            'update': ['pedido', 'guia', 'hub', 'usuario', 'reclamo'],
            'delete': ['pedido', 'guia', 'hub', 'usuario', 'reclamo'],
            'special': ['assign_mensajero', 'approve_reclamo']
        },
        'MENSAJERO': {
            'create': [],
            'read': ['pedido', 'guia'],
            'update': ['pedido', 'guia'],
            'delete': [],
            'special': ['update_tracking']
        },
        'CLIENTE': {
            'create': ['pedido', 'reclamo'],
            'read': ['pedido', 'guia', 'reclamo'],
            'update': ['pedido', 'reclamo'],
            'delete': ['pedido'],
            'special': []
        },
        'PROVEEDOR': {
            'create': [],
            'read': ['pedido', 'guia'],
            'update': ['guia'],
            'delete': [],
            'special': []
        }
    }
    
    def get_user_role(self, user):
        """Obtener rol del usuario de forma segura"""
        if not user or not user.is_authenticated:
            return None
        
        if hasattr(user, 'rol') and user.rol:
            return user.rol.tipo_rol
        
        # Fallback para usuarios sin rol asignado
        if user.is_superuser:
            return 'ADMIN'
        elif user.is_staff:
            return 'MENSAJERO'
        else:
            return 'CLIENTE'
    
    def has_permission(self, request, view):
        """Verificar permiso básico según rol y acción"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        if not user_role:
            return False
        
        action = getattr(view, 'action', 'read')
        resource = self.get_resource_from_view(view)
        
        permissions = self.ROLE_PERMISSIONS.get(user_role, {})
        allowed_actions = permissions.get(action, [])
        
        return resource in allowed_actions or action in allowed_actions
    
    def has_object_permission(self, request, view, obj):
        """Verificar permiso sobre objeto específico"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        if not user_role:
            return False
        
        # Admin tiene acceso total
        if user_role == 'ADMIN':
            return True
        
        # Verificar propiedad del objeto
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        elif hasattr(obj, 'reclamante'):
            return obj.reclamante == request.user
        elif hasattr(obj, 'pedido'):
            return obj.pedido.usuario == request.user
        
        return False
    
    def get_resource_from_view(self, view):
        """Extraer tipo de recurso del ViewSet"""
        viewset_name = view.__class__.__name__.lower()
        
        if 'pedido' in viewset_name:
            return 'pedido'
        elif 'guia' in viewset_name:
            return 'guia'
        elif 'hub' in viewset_name:
            return 'hub'
        elif 'usuario' in viewset_name:
            return 'usuario'
        elif 'reclamo' in viewset_name:
            return 'reclamo'
        
        return 'read'  # Default a read si no se puede determinar


class IsAdminUser(BaseRolePermission):
    """Permiso solo para administradores"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) == 'ADMIN'


class IsMensajero(BaseRolePermission):
    """Permiso solo para mensajeros"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) == 'MENSAJERO'


class IsCliente(BaseRolePermission):
    """Permiso solo para clientes"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) == 'CLIENTE'


class IsProveedor(BaseRolePermission):
    """Permiso solo para proveedores"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self.get_user_role(request.user) == 'PROVEEDOR'


class IsOwnerOrAdmin(BaseRolePermission):
    """Permiso para dueños del objeto o administradores"""
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        if user_role == 'ADMIN':
            return True
        
        # Verificar propiedad del objeto
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        elif hasattr(obj, 'reclamante'):
            return obj.reclamante == request.user
        elif hasattr(obj, 'pedido'):
            return obj.pedido.usuario == request.user
        
        return False


class CanCreatePedido(BaseRolePermission):
    """Permiso para crear pedidos"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        permissions = self.ROLE_PERMISSIONS.get(user_role, {})
        return 'pedido' in permissions.get('create', [])


class CanManageUsers(BaseRolePermission):
    """Permiso para gestionar usuarios"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        return user_role == 'ADMIN'


class CanManageReclamos(BaseRolePermission):
    """Permiso para gestionar reclamos"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = self.get_user_role(request.user)
        permissions = self.ROLE_PERMISSIONS.get(user_role, {})
        return 'reclamo' in permissions.get('update', [])

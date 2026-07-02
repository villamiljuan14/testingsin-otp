from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.es_admin()
        )


class IsNovedadesManager(permissions.BasePermission):
    """Permiso para gestores de novedades"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.es_admin() or 
                (request.user.rol and request.user.rol.tipo_rol in ['ADMIN', 'NOVEDADES_MANAGER'])
            )
        )
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.es_admin()
        )


class IsFleetManager(permissions.BasePermission):
    """Permiso para gestores de flota"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.es_admin() or 
                (request.user.rol and request.user.rol.tipo_rol == 'FLEET_MANAGER')
            )
        )


class IsConductor(permissions.BasePermission):
    """Permiso solo para conductores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.es_mensajero()
        )


class IsRoutePlanner(permissions.BasePermission):
    """Permiso para planificadores de rutas"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.es_admin() or 
                (request.user.rol and request.user.rol.tipo_rol in ['PLANIFICADOR', 'FLEET_MANAGER'])
            )
        )
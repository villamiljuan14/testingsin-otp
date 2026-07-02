from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from apps.Autenticacion.models import TipoRol

def role_required(*allowed_roles):
    """
    Decorador para verificar si el usuario tiene uno de los roles permitidos.
    Bloquea el acceso (403 Forbidden) si el usuario no tiene el rol correcto.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if hasattr(request.user, 'rol'):
                user_rol_val = request.user.rol.tipo_rol
                user_rol_label = getattr(request.user.rol, 'get_tipo_rol_display', lambda: None)()

                # Soporte para valores de TipoRol (ADMIN) y etiquetas humanas (Administrador)
                if user_rol_val in allowed_roles or user_rol_label in allowed_roles:
                    return view_func(request, *args, **kwargs)

                # Permite admin global por valor o etiqueta
                if user_rol_val == TipoRol.ADMINISTRADOR or user_rol_label == TipoRol.ADMINISTRADOR.label:
                    return view_func(request, *args, **kwargs)

            raise PermissionDenied("No tienes permisos para acceder a esta área.")
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorador específico para requerir rol de Administrador."""
    return role_required(TipoRol.ADMINISTRADOR)(view_func)


def admin_or_permission(permission_codename):
    """
    Decorador que permite acceso si el usuario es ADMIN o tiene el permiso especificado.
    Útil para vistas administrativas que deben ser accesibles para admins sin verificar permisos.
    
    Uso: @admin_or_permission('change_usuario')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Superusuario de Django también debe tener acceso automático
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Si es admin (rol) tiene acceso automático
            if hasattr(request.user, 'rol') and request.user.rol.tipo_rol == TipoRol.ADMINISTRADOR:
                return view_func(request, *args, **kwargs)

            # Si no es admin, verificar el permiso específico
            if request.user.has_perm(f'Autenticacion.{permission_codename}'):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("No tienes permisos para acceder a esta vista.")
        return _wrapped_view
    return decorator

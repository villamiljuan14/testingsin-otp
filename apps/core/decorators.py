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

            if hasattr(request.user, 'rol') and request.user.rol:
                user_rol_val = request.user.rol.tipo_rol
                user_rol_label = request.user.rol.get_tipo_rol_display()

                print("========== ROLE_REQUIRED ==========")
                print("Usuario:", request.user)
                print("Rol:", request.user.rol.nombre_rol)
                print("Valor BD:", user_rol_val)
                print("Display:", user_rol_label)
                print("Permitidos:", allowed_roles)
                print("Enum ADMIN:", TipoRol.ADMINISTRADOR)
                print("===================================")

                if user_rol_val in allowed_roles or user_rol_label in allowed_roles:
                    print("✔ Acceso permitido por role_required")
                    return view_func(request, *args, **kwargs)

                if (
                    user_rol_val == TipoRol.ADMINISTRADOR
                    or user_rol_label == TipoRol.ADMINISTRADOR.label
                ):
                    print("✔ Acceso permitido por ADMIN global")
                    return view_func(request, *args, **kwargs)

            print("❌ Acceso denegado por role_required")
            raise PermissionDenied("No tienes permisos para acceder a esta área.")

        return _wrapped_view

    return decorator


def admin_required(view_func):
    """
    Decorador específico para administradores.
    """
    return role_required(TipoRol.ADMINISTRADOR)(view_func)


def admin_or_permission(permission_codename):
    """
    Permite acceso si el usuario es administrador
    o tiene el permiso indicado.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            print("\n=========== ADMIN_OR_PERMISSION ===========")
            print("Usuario:", request.user)
            print("is_authenticated:", request.user.is_authenticated)
            print("is_superuser:", request.user.is_superuser)

            # Superusuario
            if request.user.is_superuser:
                print("✔ Es superusuario")
                return view_func(request, *args, **kwargs)

            # Rol
            if hasattr(request.user, 'rol') and request.user.rol:

                user_rol_val = request.user.rol.tipo_rol
                user_rol_label = request.user.rol.get_tipo_rol_display()

                print("Nombre Rol:", request.user.rol.nombre_rol)
                print("Valor BD:", user_rol_val)
                print("Display:", user_rol_label)
                print("Enum ADMIN:", TipoRol.ADMINISTRADOR)
                print("Label ADMIN:", TipoRol.ADMINISTRADOR.label)

                if (
                    user_rol_val == TipoRol.ADMINISTRADOR
                    or user_rol_label == TipoRol.ADMINISTRADOR.label
                ):
                    print("✔ Acceso permitido por rol ADMIN")
                    return view_func(request, *args, **kwargs)

            permiso = f"Autenticacion.{permission_codename}"

            print("Permiso requerido:", permiso)
            print("Tiene permiso:", request.user.has_perm(permiso))
            print("===========================================")

            if request.user.has_perm(permiso):
                print("✔ Acceso permitido por permiso")
                return view_func(request, *args, **kwargs)

            print("❌ Acceso denegado")
            raise PermissionDenied("No tienes permisos para acceder a esta vista.")

        return _wrapped_view

    return decorator

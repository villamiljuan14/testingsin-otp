from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.rol import Rol
from .models.choices import TipoRol

Usuario = get_user_model()

# ──────────────────────────────────────────────────────────
# CONFIGURACIÓN DE SEÑALES - AUTENTICACIÓN STATALESS (JWT)
# ──────────────────────────────────────────────────────────
# Nota: Se eliminó el receptor de rest_framework.authtoken.Token
# debido a que SimpleJWT firma y valida tokens en memoria (on-demand).

@receiver(pre_save, sender=Usuario)
def asignar_rol_por_defecto(sender, instance, **kwargs):
    """
    Asigna el rol de Cliente por defecto si el usuario es nuevo y no tiene uno.
    Se ejecuta en memoria ANTES del INSERT en la DB, ahorrando un UPDATE redundante.
    """
    # Verificamos si es un registro nuevo (no tiene clave primaria aún) y no tiene rol
    if not instance.pk and not instance.rol:
        try:
            # Buscamos el rol de Cliente o lo creamos si no existe en la base de datos
            rol_cliente, _ = Rol.objects.get_or_create(
                nombre_rol='Cliente',
                defaults={'tipo_rol': TipoRol.CLIENTE, 'activo': True}
            )
            # Asignamos directamente en memoria. Django lo incluirá en el INSERT original.
            instance.rol = rol_cliente
            
        except Exception:
            # Evita que falle el flujo de registro si se corren pruebas o 
            # si las tablas de la base de datos no se han migrado completamente.
            pass
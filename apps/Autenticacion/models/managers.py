from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, email, primer_nombre, primer_apellido, doc_usuario, password=None, **extra_fields):
        if not email:
            raise ValueError(_('El Email es obligatorio'))
        if not doc_usuario:
            raise ValueError(_('El documento es obligatorio'))
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            primer_nombre=primer_nombre,
            primer_apellido=primer_apellido,
            doc_usuario=doc_usuario,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, primer_nombre, primer_apellido, doc_usuario, password=None, **extra_fields):
        # Evitamos la importación circular trayendo el modelo Rol en tiempo de ejecución
        from .rol import Rol
        from .choices import TipoRol

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser debe tener is_superuser=True.'))
            
        # ──────────────────────────────────────────────────────────
        # MUTACIÓN DE INTEGRACIÓN: Asignación automática de Rol Admin
        # ──────────────────────────────────────────────────────────
        if 'rol' not in extra_fields or extra_fields['rol'] is None:
            try:
                # Buscamos o creamos el rol administrativo en la base de datos de Supabase
                rol_admin, _ = Rol.objects.get_or_create(
                    nombre_rol='Administrador',
                    defaults={'tipo_rol': 'ADMINISTRADOR', 'activo': True}
                )
                extra_fields['rol'] = rol_admin
            except Exception:
                # Si las tablas no existen todavía durante el primer 'migrate', 
                # permitimos que continúe para no bloquear el despliegue inicial
                pass
        
        return self.create_user(email, primer_nombre, primer_apellido, doc_usuario, password, **extra_fields)
    
    def activos(self):
        """
        QuerySet de acceso rápido para filtrar usuarios activos.
        Uso: Usuario.objects.activos()
        """
        return self.filter(is_active=True)
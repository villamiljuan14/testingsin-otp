from django.db import models
from .choices import TipoRol


class Rol(models.Model):
    """
    Modelo para la gestión de roles de usuario en el sistema de logística.
    Controla el tipo de acceso operativo y administrativo.
    """
    
    nombre_rol = models.CharField(max_length=50, unique=True)
    
    # CORRECCIÓN: Quitamos null/blank y exigimos un valor por defecto para asegurar la integridad
    tipo_rol = models.CharField(
        max_length=50, 
        choices=TipoRol.choices, 
        default=TipoRol.CLIENTE
    )
    
    descripcion = models.TextField(blank=True, help_text='Descripción del rol')
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre_rol']

    def __str__(self):
        return self.nombre_rol

    # ──────────────────────────────────────────────────────────
    # MÉTODOS HELPERS DE INSTANCIA
    # ──────────────────────────────────────────────────────────
    
    def es_administrativo(self) -> bool:
        """Determina si el rol pertenece a la capa de administración."""
        return self.activo and self.tipo_rol == TipoRol.ADMINISTRADOR

    def es_operativo(self) -> bool:
        """Determina si el rol pertenece a los mensajeros en campo."""
        return self.activo and self.tipo_rol == TipoRol.MENSAJERO

    def es_usuario_final(self) -> bool:
        """Determina si el rol pertenece a un cliente estándar."""
        return self.activo and self.tipo_rol == TipoRol.CLIENTE
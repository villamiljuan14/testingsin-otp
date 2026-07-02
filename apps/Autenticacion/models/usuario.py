from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .choices import TipoDocumento, EstadoUsuario
from .managers import UsuarioManager
from .rol import Rol

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    tipo_documento = models.CharField(max_length=10, choices=TipoDocumento.choices, default=TipoDocumento.CC)
    doc_usuario = models.CharField(max_length=25, unique=True, db_index=True)
    primer_nombre = models.CharField(max_length=80)
    segundo_nombre = models.CharField(max_length=80, null=True, blank=True)
    primer_apellido = models.CharField(max_length=80)
    segundo_apellido = models.CharField(max_length=80, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) 
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True, related_name='usuarios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    intentos_login_fallidos = models.PositiveIntegerField(default=0)
    bloqueo_hasta = models.DateTimeField(null=True, blank=True)
    ultimo_login_ip = models.GenericIPAddressField(null=True, blank=True)
   
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['primer_nombre', 'primer_apellido', 'doc_usuario']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['doc_usuario']),
            models.Index(fields=['is_active', 'is_staff']),
        ]

    def __str__(self):
        return f'{self.nombre_completo} ({self.email})'
    
    @property
    def nombre_completo(self):
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        apellidos = [self.primer_apellido]
        if self.segundo_apellido:
            apellidos.append(self.segundo_apellido)
        return f"{' '.join(nombres)} {' '.join(apellidos)}"
    
    def get_full_name(self):
        return self.nombre_completo

    def get_short_name(self):
        return self.primer_nombre

    @property
    def estado(self):
        if not self.is_active:
            return EstadoUsuario.INACTIVO
        if self.esta_bloqueado():
            return EstadoUsuario.BLOQUEADO
        return EstadoUsuario.ACTIVO

    @property
    def estado_usuario(self):
        """Compatibilidad con consultas antiguas y templates que usan estado_usuario."""
        return self.estado == EstadoUsuario.ACTIVO

    def esta_bloqueado(self):
        """Evaluación pura y de solo lectura sobre el estado de bloqueo actual."""
        if self.bloqueo_hasta and timezone.now() < self.bloqueo_hasta:
            return True
        return False

    def registrar_login_fallido(self):
        """Registra un intento fallido y calcula si aplica penalización de tiempo."""
        self.intentos_login_fallidos += 1
        lockout_attempts = getattr(settings, 'LOGIN_FAILED_MAX_ATTEMPTS', 5)
        if self.intentos_login_fallidos >= lockout_attempts:
            lock_minutes = getattr(settings, 'LOGIN_LOCK_MINUTES', 1 if settings.DEBUG else 15)
            self.bloqueo_hasta = timezone.now() + timedelta(minutes=lock_minutes)
        self.save(update_fields=['intentos_login_fallidos', 'bloqueo_hasta'])

    def registrar_login_exitoso(self, ip=None):
        """Limpia todo rastro de bloqueos previos tras un acceso correcto."""
        self.intentos_login_fallidos = 0
        self.bloqueo_hasta = None
        self.ultimo_login_ip = ip
        self.save(update_fields=['intentos_login_fallidos', 'bloqueo_hasta', 'ultimo_login_ip'])
    
    def es_admin(self):
        return self.is_staff or (hasattr(self, 'rol') and self.rol and self.rol.tipo_rol == 'ADMINISTRADOR')
    
    def es_mensajero(self):
        return hasattr(self, 'rol') and self.rol and self.rol.tipo_rol == 'MENSAJERO'
    
    def es_cliente(self):
        return hasattr(self, 'rol') and self.rol and self.rol.tipo_rol == 'CLIENTE'
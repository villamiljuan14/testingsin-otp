from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from apps.Autenticacion.models.usuario import Usuario
from apps.Autenticacion.models.rol import Rol
from apps.Autenticacion.validators import validar_documento, validar_telefono
from apps.Autenticacion.forms import UsuarioForm  


class CustomUserCreationForm(UserCreationForm):
    """Formulario específico para la creación limpia de usuarios desde el Admin"""
    class Meta:
        model = Usuario
        fields = ('email', 'primer_nombre', 'primer_apellido', 'tipo_documento', 'doc_usuario', 'rol')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioForm  
    add_form = CustomUserCreationForm
    
    list_display = ['email', 'nombre_completo', 'rol', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'rol__tipo_rol']
    search_fields = ['email', 'doc_usuario', 'primer_nombre', 'primer_apellido']
    ordering = ['email']
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'intentos_login_fallidos', 'bloqueo_hasta', 'ultimo_login_ip']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Información Personal'), {
            'fields': (
                'tipo_documento', 'doc_usuario', 
                'primer_nombre', 'segundo_nombre', 
                'primer_apellido', 'segundo_apellido', 
                'telefono', 'rol'
            )
        }),
        (_('Permisos'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Seguridad'), {
            'fields': (
                'intentos_login_fallidos', 
                'bloqueo_hasta', 
                'ultimo_login_ip'       
            )
        }),
        (_('Auditoría'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'primer_nombre', 'primer_apellido', 
                'tipo_documento', 'doc_usuario', 'rol', 'password'
            ),
        }),
    )


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre_rol', 'tipo_rol', 'activo']
    list_filter = ['tipo_rol', 'activo']
    search_fields = ['nombre_rol']
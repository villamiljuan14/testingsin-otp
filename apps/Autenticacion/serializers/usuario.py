from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models.rol import Rol

Usuario = get_user_model()


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre_rol', 'tipo_rol', 'descripcion', 'activo']


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    rol = RolSerializer(read_only=True)
    estado = serializers.ReadOnlyField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre_completo', 'tipo_documento', 
            'doc_usuario', 'telefono', 'rol', 'estado', 
            'two_factor_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'doc_usuario', 'created_at', 'updated_at']


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['telefono', 'segundo_nombre', 'segundo_apellido']
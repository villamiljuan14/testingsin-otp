from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
# Cambiamos el Token clásico por RefreshToken de SimpleJWT
from rest_framework_simplejwt.tokens import RefreshToken
from ..models.choices import TipoDocumento

Usuario = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email y contraseña son requeridos')
        
        email = Usuario.objects.normalize_email(email.strip())
        password = password.strip()
        try:
            user = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Credenciales inválidas')
        
        # 1. Control de seguridad por intentos fallidos
        if not user.check_password(password):
            user.registrar_login_fallido()
            raise serializers.ValidationError('Credenciales inválidas')
        
        # 2. Control de bloqueos por seguridad / fuerza bruta
        if hasattr(user, 'esta_bloqueado') and user.esta_bloqueado():
            bloqueo_hasta = getattr(user, 'bloqueo_hasta', None)
            if bloqueo_hasta:
                minutos_restantes = max(1, int((bloqueo_hasta - timezone.now()).total_seconds() // 60))
                raise serializers.ValidationError(
                    f'Usuario bloqueado temporalmente. Intenta de nuevo en {minutos_restantes} minutos.'
                )
        # 3. Control de estado activo
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo. Contacte al administrador.')
        
        # Registrar auditoría de IP de forma segura
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else '0.0.0.0'
        if hasattr(user, 'registrar_login_exitoso'):
            user.registrar_login_exitoso(ip=ip_address)
        
        # 4. Generar JWT para autenticación
        refresh = RefreshToken.for_user(user)
        
        # Retornamos la estructura compatible con JWT que espera tu frontend
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    tipo_documento = serializers.ChoiceField(choices=TipoDocumento.choices)
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'password', 'tipo_documento', 'doc_usuario',
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 
            'segundo_apellido', 'telefono'
        ]
    
    def create(self, validated_data):
        # Al usar create_user, Django automáticamente setea is_active=True por defecto
        # asegurando que el usuario pueda pasar el primer paso del LoginSerializer.
        user = Usuario.objects.create_user(**validated_data)
        return user
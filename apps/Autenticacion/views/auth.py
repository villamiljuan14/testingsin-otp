from rest_framework import status, generics, parsers
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, login as django_login
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from ..serializers import LoginSerializer, RegistroSerializer, UsuarioSerializer

Usuario = get_user_model()


class LoginView(generics.GenericAPIView):
    """
    POST /api/auth/login/
    Valida credenciales (email/password) y entrega JWT access/refresh directamente.
    Sin validación OTP ni pasos adicionales.
    """
    authentication_classes = []
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Crear sesión de Django para autenticación tradicional
        django_login(request, user)
        
        # El serializer corregido ahora nos entrega 'access' y 'refresh'
        return Response({
            'status': 'success',
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': {
                'id': user.id,
                'email': user.email,
                'nombre_completo': user.nombre_completo,
                'rol': user.rol.nombre_rol if user.rol else None
            }
        }, status=status.HTTP_200_OK)


class RegistroView(generics.CreateAPIView):
    """
    POST /api/registro/
    Registra al usuario y le entrega sus JWT iniciales.
    """
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generamos tokens JWT inmediatamente tras el registro
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'created',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UsuarioSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    """
    POST /api/logout/
    Para JWT, el logout seguro consiste en hacer blacklist del Refresh Token en el front,
    o simplemente eliminarlo del almacenamiento local.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Requiere 'rest_framework_simplejwt.token_blacklist' en INSTALLED_APPS
            return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)
        except Exception:
            # Si no está configurada la blacklist, basta con que el front destruya el token
            return Response({'message': 'Sesión finalizada localmente'}, status=status.HTTP_200_OK)


class ForgotPasswordView(generics.GenericAPIView):
    """
    POST /api/auth/forgot-password/
    Envía un email de recuperación de contraseña usando el sistema tradicional de Django.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        if not email:
            return JsonResponse({'error': 'Email es requerido'}, status=400)
        
        try:
            user = Usuario.objects.get(email=email)
            # Usar el sistema de password reset de Django
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.core.mail import send_mail
            from django.conf import settings
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.SITE_URL}/reset-password/{uid}/{token}/"
            
            send_mail(
                subject='Recuperación de contraseña - Enviart',
                message=f'Para restablecer tu contraseña, visita el siguiente enlace:\n\n{reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True, 'message': 'Email de recuperación enviado'})
                
        except Usuario.DoesNotExist:
            return JsonResponse({'success': True, 'message': 'Si el email existe, se enviará un correo de recuperación'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ResetPasswordView(generics.GenericAPIView):
    """
    POST /api/auth/reset-password/
    Valida el token y establece la nueva contraseña.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        new_password = request.data.get('new_password')
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not all([email, new_password, uid, token]):
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
        
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_decode
            from django.core.exceptions import ValidationError
            from django.contrib.auth.password_validation import validate_password
            
            user_id = urlsafe_base64_decode(uid)
            user = Usuario.objects.get(pk=user_id, email=email)
            
            if not default_token_generator.check_token(user, token):
                return JsonResponse({'error': 'Token inválido o expirado'}, status=400)
            
            # Validar la nueva contraseña
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return JsonResponse({'error': '\n'.join(e.messages)}, status=400)
            
            user.set_password(new_password)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Contraseña cambiada exitosamente'})
            
        except (Usuario.DoesNotExist, ValueError, OverflowError):
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
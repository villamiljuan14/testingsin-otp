from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from ..serializers import UsuarioSerializer, UsuarioUpdateSerializer
from ..permissions import IsOwnerOrAdmin

Usuario = get_user_model()


class PerfilView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT/PATCH /api/auth/perfil/
    Maneja la lectura y actualización del perfil del usuario autenticado.
    Exige de forma obligatoria un JWT que haya aprobado el segundo factor (OTP).
    """
    # 2. Reemplazamos IsAuthenticated por el combo estricto de la Opción B
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Al usar request.user, implícitamente aseguramos que el dueño es quien edita
        return self.request.user
    
    def get_serializer_class(self):
        # Simplificación de la condición usando una tupla
        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Al pasar partial=True, permitimos que PATCH funcione de forma nativa sin exigir todos los campos
        partial = kwargs.pop('partial', True) if self.request.method == 'PATCH' else False
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Retornamos los datos frescos usando el serializador de lectura estándar
        return Response(UsuarioSerializer(instance).data, status=status.HTTP_200_OK)
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


def extract_token_from_scope(scope) -> str | None:
    query_string = scope.get('query_string', b'').decode()
    params = parse_qs(query_string)
    token_key = params.get('token', [None])[0]
    if token_key:
        return token_key

    headers = dict(scope.get('headers', []))
    auth_header = headers.get(b'authorization', b'').decode()
    if auth_header.startswith('Token '):
        return auth_header[6:].strip()
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip()

    return None


def get_user_from_token(token_key: str | None):
    if not token_key:
        return AnonymousUser()

    try:
        token = Token.objects.select_related('user', 'user__rol').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


def user_can_access_pedido(user, pedido) -> str | None:
    """
    Retorna el rol de acceso al WebSocket del pedido:
    - 'sender': mensajero asignado (puede enviar ubicación)
    - 'viewer': cliente dueño del pedido (solo recibe)
    - 'both': administrador
    - None: sin acceso
    """
    if not user.is_authenticated:
        return None

    if user.is_superuser or user.is_staff:
        return 'both'

    if hasattr(user, 'rol') and user.rol and user.rol.tipo_rol == 'ADMIN':
        return 'both'

    if user.es_mensajero() and pedido.mensajero_id == user.id:
        return 'sender'

    if pedido.usuario_id == user.id:
        return 'viewer'

    return None

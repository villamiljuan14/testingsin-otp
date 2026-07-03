from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser


def extract_token_from_scope(scope) -> str | None:
    """Extrae el token del query string o del header Authorization."""
    query_string = scope.get('query_string', b'').decode()
    params = parse_qs(query_string)
    token_key = params.get('token', [None])[0]
    if token_key:
        return token_key

    headers = dict(scope.get('headers', []))
    auth_header = headers.get(b'authorization', b'').decode()
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip()
    if auth_header.startswith('Token '):
        return auth_header[6:].strip()

    return None


def get_user_from_token(token_key: str | None):
    """
    Resuelve el usuario desde un JWT access token (SimpleJWT).
    Fallback a DRF Token para compatibilidad con clientes legacy.
    """
    if not token_key:
        return AnonymousUser()

    # ── Intentar como JWT (SimpleJWT) ────────────────────────────────────────
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth import get_user_model

        validated = AccessToken(token_key)
        user_id = validated['user_id']
        User = get_user_model()
        return User.objects.select_related('rol').get(pk=user_id)
    except Exception:
        pass

    # ── Fallback: DRF Token ───────────────────────────────────────────────────
    try:
        from rest_framework.authtoken.models import Token
        token = Token.objects.select_related('user', 'user__rol').get(key=token_key)
        return token.user
    except Exception:
        pass

    return AnonymousUser()


def user_can_access_pedido(user, pedido) -> str | None:
    """
    Retorna el rol de acceso al WebSocket:
    - 'sender' : mensajero asignado (puede enviar ubicación GPS)
    - 'viewer' : cliente dueño del pedido (solo recibe broadcasts)
    - 'both'   : administrador (envía y recibe)
    - None     : sin acceso
    """
    if not user.is_authenticated:
        return None

    if user.is_superuser or user.is_staff:
        return 'both'

    if hasattr(user, 'rol') and user.rol and user.rol.tipo_rol in ('ADMIN', 'ADMINISTRADOR'):
        return 'both'

    if user.es_mensajero() and pedido.mensajero_id == user.id:
        return 'sender'

    if pedido.usuario_id == user.id:
        return 'viewer'

    return None

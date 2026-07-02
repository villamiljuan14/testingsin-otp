import json
import logging
from datetime import datetime, timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from apps.Pedidos.models import HistorialUbicacion, Pedido
from apps.Pedidos.ws_auth import extract_token_from_scope, get_user_from_token, user_can_access_pedido

logger = logging.getLogger(__name__)


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket de rastreo en vivo por pedido.

    URL: ws://host/ws/tracking/<pedido_id>/?token=<drf_token>

    - Mensajero asignado: envía {type, lat, lng, accuracy?, timestamp?}
    - Cliente del pedido / admin: reciben broadcasts del grupo order_<id>
    """

    async def connect(self):
        self.pedido_id = self.scope['url_route']['kwargs']['pedido_id']
        self.room_group_name = f'order_{self.pedido_id}'
        self.access_role = None

        token_key = extract_token_from_scope(self.scope)
        self.user = await self._resolve_user(token_key)

        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        pedido = await self._get_pedido(self.pedido_id)
        if pedido is None:
            await self.close(code=4004)
            return

        self.access_role = await self._resolve_access_role(pedido)
        if self.access_role is None:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        logger.info(
            'WS tracking conectado pedido=%s user=%s role=%s',
            self.pedido_id,
            self.user.id,
            self.access_role,
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if self.access_role not in ('sender', 'both'):
            return

        try:
            data = json.loads(text_data)
        except (TypeError, json.JSONDecodeError):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'JSON inválido',
            }))
            return

        if data.get('type') != 'location_update':
            return

        lat = data.get('lat')
        lng = data.get('lng')
        if lat is None or lng is None:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'lat y lng son requeridos',
            }))
            return

        payload = {
            'type': 'location_update',
            'pedido_id': int(self.pedido_id),
            'lat': float(lat),
            'lng': float(lng),
            'accuracy': data.get('accuracy'),
            'timestamp': data.get('timestamp') or datetime.now(timezone.utc).isoformat(),
        }

        await self._save_location(payload)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'tracking_update',
                'payload': payload,
            },
        )

    async def tracking_update(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    @database_sync_to_async
    def _resolve_user(self, token_key):
        return get_user_from_token(token_key)

    @database_sync_to_async
    def _get_pedido(self, pedido_id):
        try:
            return Pedido.objects.select_related('mensajero', 'usuario').get(pk=pedido_id)
        except Pedido.DoesNotExist:
            return None

    @database_sync_to_async
    def _resolve_access_role(self, pedido):
        return user_can_access_pedido(self.user, pedido)

    @database_sync_to_async
    def _save_location(self, payload):
        HistorialUbicacion.objects.create(
            pedido_id=payload['pedido_id'],
            latitud=payload['lat'],
            longitud=payload['lng'],
            precision_gps=payload.get('accuracy'),
        )

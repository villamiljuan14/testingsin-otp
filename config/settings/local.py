from .base import *

# ── Redis en WSL ──────────────────────────────────────────────────────────────
# WSL expone Redis en su IP interna. Si cambia tras reiniciar WSL,
# actualiza con: wsl hostname -I
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('172.25.189.151', 6379)],
        },
    },
}

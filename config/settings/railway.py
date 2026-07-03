"""
Configuración específica para despliegue en Railway
Optimizado para producción con OTP y JWT
"""
from .base import *
import os
import dj_database_url

# =============================================
# DEBUG y Seguridad
# =============================================
DEBUG = False

# Railway proporciona el hostname externo
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

# Construir ALLOWED_HOSTS dinámicamente para Railway
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
]

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
if RAILWAY_STATIC_URL:
    # Extraer dominio de URL estática si existe
    from urllib.parse import urlparse
    parsed = urlparse(RAILWAY_STATIC_URL)
    if parsed.hostname:
        ALLOWED_HOSTS.append(parsed.hostname)

# =============================================
# Security Settings for Production
# =============================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Railway maneja SSL en el proxy, no en la app
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = []

# Agregar orígenes confiables dinámicamente
for host in ALLOWED_HOSTS:
    if host not in ['localhost', '127.0.0.1']:
        CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
        CSRF_TRUSTED_ORIGINS.append(f'http://{host}')

# =============================================
# WhiteNoise para archivos estáticos
# =============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar después de SecurityMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# =============================================
# Base de datos (Railway PostgreSQL)
# =============================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# =============================================
# Redis para Channels y Cache (Railway Redis)
# =============================================
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'capacity': 1500,  # Capacidad aumentada para producción
            'expiry': 10,      # Expiración más corta para mejor rendimiento
        },
    },
}

# Cache de Django usando Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# =============================================
# Logging para producción
# =============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'enviart.otp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'enviart.auth': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================
# Configuración OTP para Producción
# =============================================
OTP_LENGTH = int(os.environ.get('OTP_LENGTH', 6))
OTP_EXPIRY_SECONDS = int(os.environ.get('OTP_EXPIRY_SECONDS', 600))
OTP_MAX_ATTEMPTS = int(os.environ.get('OTP_MAX_ATTEMPTS', 3))
OTP_RESEND_COOLDOWN = int(os.environ.get('OTP_RESEND_COOLDOWN', 60))
OTP_APP_NAME = os.environ.get('OTP_APP_NAME', 'Enviart')
OTP_DEBUG_CODE = None  # Deshabilitar código fijo en producción

# =============================================
# JWT Settings para Producción
# =============================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'pk',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# =============================================
# CORS para Producción
# =============================================
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') 
    if origin.strip()
]

# Si no hay orígenes específicos, usar los dominios de Railway
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        "https://*.railway.app",
        "https://*.up.railway.app",
    ]

CORS_ALLOW_CREDENTIALS = True

# =============================================
# Rate Limiting (Opcional - requiere django-ratelimit)
# =============================================
# Para agregar rate limiting en producción, instalar django-ratelimit
# y configurar en las vistas de autenticación

# =============================================
# Health Check Endpoint
# =============================================
# Útil para monitoreo en Railway
HEALTH_CHECK_ENABLED = True

import environ
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    'enviart-web-j7nx.onrender.com',
    'localhost',
    '127.0.0.1',
    '*'
])

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    # Apps locales - ordenadas por dependencias
    'apps.core',
    'apps.Autenticacion',
    'apps.Ubicaciones',
    'apps.Pedidos',
    'apps.Personal',
    'apps.Novedades',
    'apps.Rutas',
    'apps.Vehiculos',
]

AUTH_USER_MODEL = 'Autenticacion.Usuario'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Paginación por defecto para todas las vistas
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Filtros y búsqueda
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Manejo de excepciones personalizado
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# Configuración específica de SimpleJWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,  # Cambiar a True en producción con Redis
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
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    "https://enviart-web-j7nx.onrender.com",
    "http://127.0.0.1:63846",
    "http://localhost:63846",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# --- Redis + Channels (usa REDIS_URL de Render) ---
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [env('REDIS_URL')],
        },
    },
}

# --- Base de datos (usa DATABASE_URL de Render) ---
#DATABASES = {
    #'default': dj_database_url.config(
        #default=env('DATABASE_URL'),
        #conn_max_age=600,
        #ssl_require=True,
    #)
#}
# --- Base de datos (Compatible con Postgres Local y Railway) ---
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Login lockout / development shortcuts ---
LOGIN_FAILED_MAX_ATTEMPTS = env.int('LOGIN_FAILED_MAX_ATTEMPTS', 5)
LOGIN_LOCK_MINUTES = env.int('LOGIN_LOCK_MINUTES', 1 if DEBUG else 15)

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- Static files ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise middleware sirve archivos estáticos directamente
# No necesitamos configurar STORAGES o STATICFILES_STORAGE especial
# Django usa el backend por defecto y WhiteNoise middleware maneja el resto


# --- Media files (Cloudinary) ---
import cloudinary

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = ''  # Cloudinary genera sus propias URLs, no necesita prefijo

# Configuración explícita de STORAGES para Django 4.2+
STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# URL del sitio para emails y enlaces
SITE_URL = env('SITE_URL', default='http://127.0.0.1:8000')

LOGIN_URL = 'login'

# --- Wompi ---
WOMPI_MODE = env('WOMPI_MODE', default='sandbox')

WOMPI_SANDBOX_PUBLIC_KEY          = env('WOMPI_SANDBOX_PUBLIC_KEY', default='')
WOMPI_SANDBOX_PRIVATE_KEY         = env('WOMPI_SANDBOX_PRIVATE_KEY', default='')
WOMPI_SANDBOX_INTEGRITY_SECRET    = env('WOMPI_SANDBOX_INTEGRITY_SECRET', default='')
WOMPI_SANDBOX_EVENTS_SECRET       = env('WOMPI_SANDBOX_EVENTS_SECRET', default='')

WOMPI_PRODUCTION_PUBLIC_KEY       = env('WOMPI_PRODUCTION_PUBLIC_KEY', default='')
WOMPI_PRODUCTION_PRIVATE_KEY      = env('WOMPI_PRODUCTION_PRIVATE_KEY', default='')
WOMPI_PRODUCTION_INTEGRITY_SECRET = env('WOMPI_PRODUCTION_INTEGRITY_SECRET', default='')
WOMPI_PRODUCTION_EVENTS_SECRET    = env('WOMPI_PRODUCTION_EVENTS_SECRET', default='')

if WOMPI_MODE == 'production':
    WOMPI_PUBLIC_KEY       = WOMPI_PRODUCTION_PUBLIC_KEY
    WOMPI_PRIVATE_KEY      = WOMPI_PRODUCTION_PRIVATE_KEY
    WOMPI_INTEGRITY_SECRET = WOMPI_PRODUCTION_INTEGRITY_SECRET
    WOMPI_EVENTS_SECRET    = WOMPI_PRODUCTION_EVENTS_SECRET
    WOMPI_API_URL          = 'https://api.wompi.co/v1'
else:
    WOMPI_PUBLIC_KEY       = WOMPI_SANDBOX_PUBLIC_KEY
    WOMPI_PRIVATE_KEY      = WOMPI_SANDBOX_PRIVATE_KEY
    WOMPI_INTEGRITY_SECRET = WOMPI_SANDBOX_INTEGRITY_SECRET
    WOMPI_EVENTS_SECRET    = WOMPI_SANDBOX_EVENTS_SECRET
    WOMPI_API_URL          = 'https://api.sandbox.wompi.co/v1'

WOMPI_WIDGET_URL   = 'https://checkout.wompi.co/widget.js'
WOMPI_CHECKOUT_URL = 'https://checkout.wompi.co/p/'

# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:63846",
    "http://127.0.0.1:63846",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG

import os
import socket

old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'onboarding@resend.dev')
OTP_FROM_EMAIL = os.environ.get('OTP_FROM_EMAIL', DEFAULT_FROM_EMAIL)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

# =============================================
# Estructura de Proyecto Django para Producción
# =============================================
# Este documento describe la estructura mejorada del proyecto
# siguiendo las mejores prácticas de Django para producción

## Estructura del Proyecto

```
Enviart/
├── config/                          # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py                      # Configuración ASGI para WebSockets
│   ├── wsgi.py                      # Configuración WSGI tradicional
│   ├── urls.py                      # URLs principales
│   ├── email_backends.py            # Backends personalizados de email
│   └── settings/                    # Configuraciones por entorno
│       ├── __init__.py              # (vacío, permite imports)
│       ├── base.py                  # Configuración común a todos los entornos
│       ├── local.py                 # Configuración para desarrollo local
│       ├── production.py            # Configuración para producción general
│       └── railway.py               # Configuración específica para Railway
│
├── apps/                            # Aplicaciones Django modularizadas
│   ├── __init__.py
│   ├── core/                        # Funcionalidades centrales
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── views/
│   │   ├── serializers/
│   │   ├── permissions.py           # Permisos personalizados
│   │   └── ...
│   │
│   └── Autenticacion/               # Módulo de autenticación (APP PRINCIPAL)
│       ├── __init__.py
│       ├── admin.py                 # Registro en Django Admin
│       ├── apps.py                  # Configuración de la app
│       ├── models/                  # Modelos organizados en paquete
│       │   ├── __init__.py
│       │   ├── usuario.py           # Modelo personalizado de Usuario
│       │   ├── rol.py               # Modelo de Roles
│       │   ├── choices.py           # Choices para modelos
│       │   └── managers.py          # Managers personalizados
│       │
│       ├── views/                   # Vistas organizadas en paquete
│       │   ├── __init__.py
│       │   ├── auth.py              # Vistas de autenticación (Login, Logout, Registro)
│       │   ├── usuario.py           # Vistas de gestión de usuarios
│       │   ├── classic.py           # Vistas tradicionales (HTML templates)
│       │   ├── cbv_usuarios.py      # Class-based views para usuarios
│       │   └── views_otp_jwt.py     # Vistas OTP + JWT (API REST)
│       │
│       ├── serializers/             # Serializadores DRF
│       │   ├── __init__.py
│       │   ├── auth.py              # Serializadores de autenticación
│       │   └── usuario.py           # Serializadores de usuario
│       │
│       ├── services/                # Capa de servicios (lógica de negocio)
│       │   ├── __init__.py
│       │   ├── base.py              # Servicios base
│       │   ├── otp_service.py       # Servicio OTP (Email + TOTP)
│       │   ├── usuario_service.py   # Servicio de usuarios
│       │   ├── validation_service.py
│       │   ├── pagination.py
│       │   └── export_service.py
│       │
│       ├── permissions/             # Permisos personalizados
│       │   ├── __init__.py
│       │   └── otp_permission.py    # Permiso OTPVerified para DRF
│       │
│       ├── forms.py                 # Formularios Django tradicionales
│       ├── signals.py               # Señales Django
│       ├── validators.py            # Validadores personalizados
│       ├── urls.py                  # URLs de la aplicación
│       └── urls_otp_jwt.py          # URLs específicas para OTP+JWT
│
├── Templates/                       # Templates HTML globales
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard/
│   ├── otp/
│   └── ...
│
├── static/                          # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                           # Archivos media (solo local, en prod usa Cloudinary)
│
├── manage.py                        # Script de administración Django
├── requirements.txt                 # Dependencias Python
├── pyproject.toml                   # Configuración del proyecto Python
├── docker-compose.yml               # Configuración Docker para desarrollo
├── .env.example                     # Ejemplo de variables de entorno
├── .env.railway.example             # Variables específicas para Railway
└── README.md                        # Documentación del proyecto
```

## Mejoras Implementadas

### 1. Separación de Configuraciones por Entorno

- **base.py**: Configuración común (INSTALLED_APPS, MIDDLEWARE, etc.)
- **local.py**: Para desarrollo local (DEBUG=True, SQLite, etc.)
- **production.py**: Para producción general (Render, otros hosts)
- **railway.py**: Optimizado específicamente para Railway

### 2. Autenticación Robusta con OTP + JWT

**Características:**
- JWT con SimpleJWT para stateless authentication
- OTP por Email (usando Resend API)
- OTP por TOTP (Google Authenticator)
- Claims personalizados en JWT (`otp_verified`, `otp_channel`)
- Permisos DRF para proteger rutas que requieren verificación OTP

**Endpoints API:**
```
POST /api/auth/login/              # Login tradicional
POST /api/auth/register/           # Registro de usuarios
POST /api/auth/logout/             # Logout
POST /api/token/refresh/           # Refresh de token JWT

# OTP Endpoints
POST /api/otp/email/send/          # Enviar OTP por email
POST /api/otp/email/verify/        # Verificar OTP por email
GET  /api/otp/totp/setup/          # Obtener QR para Google Authenticator
POST /api/otp/totp/setup/          # Confirmar activación TOTP
POST /api/otp/totp/verify/         # Verificar código TOTP
POST /api/otp/totp/disable/        # Desactivar TOTP
```

### 3. Estructura Modular de la App de Autenticación

**Organización por capas:**
- **Models**: Separados en submódulos (usuario.py, rol.py, choices.py, managers.py)
- **Views**: Organizadas por tipo (auth.py, usuario.py, classic.py, views_otp_jwt.py)
- **Services**: Lógica de negocio reutilizable (otp_service.py, usuario_service.py)
- **Serializers**: Exclusivos para API REST
- **Permissions**: Permisos personalizados (otp_permission.py)

### 4. Configuración Optimizada para Railway

**Variables de entorno detectadas automáticamente:**
- `RAILWAY_PROJECT_ID`
- `RAILWAY_SERVICE_NAME`
- `RAILWAY_PUBLIC_DOMAIN`

**Configuraciones específicas:**
- ALLOWED_HOSTS dinámico basado en dominios de Railway
- CSRF_TRUSTED_ORIGINS configurado automáticamente
- Logging optimizado para producción
- Cache Redis configurado
- Rate limiting ready (requiere django-ratelimit)

### 5. Seguridad Mejorada

**Implementado:**
- HTTPS forzado en producción
- Cookies seguras (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- Protección contra XSS y CSRF
- Rate limiting en endpoints de autenticación
- Lockout después de intentos fallidos
- Hash seguro de códigos OTP
- Tokens JWT con expiración configurada

### 6. Manejo de Archivos Estáticos y Media

**Estáticos (WhiteNoise):**
- Compresión automática
- Cacheo agresivo
- Servidos directamente desde el contenedor

**Media (Cloudinary):**
- Almacenamiento en la nube
- Transformaciones de imágenes
- CDN incluido

## Flujo de Autenticación con OTP

### Flujo Email OTP:

1. Usuario envía credenciales → `/api/auth/login/`
2. Si tiene OTP habilitado, recibe respuesta `otp_required: true`
3. Cliente solicita envío de OTP → `POST /api/otp/email/send/`
4. Usuario recibe email con código de 6 dígitos
5. Cliente envía código → `POST /api/otp/email/verify/`
6. Servidor verifica y devuelve JWT con claim `otp_verified: true`
7. Cliente usa JWT para acceder a rutas protegidas

### Flujo TOTP (Google Authenticator):

1. Usuario autenticado solicita activar TOTP → `GET /api/otp/totp/setup/`
2. Servidor devuelve QR code en base64
3. Usuario escanea QR con Google Authenticator
4. Cliente envía primer código → `POST /api/otp/totp/setup/`
5. Servidor confirma y guarda secreto, devuelve JWT verificado
6. Próximos logins requieren código TOTP → `POST /api/otp/totp/verify/`

## Comandos Útiles

### Desarrollo Local:
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Ejecutar servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar estáticos
python manage.py collectstatic --no-input
```

### Producción (Railway):
```bash
# Las migraciones se ejecutan automáticamente en pre-deploy
# El comando de inicio es:
daphne config.asgi:application --port $PORT --bind 0.0.0.0
```

## Variables de Entorno Requeridas

Ver `.env.railway.example` para lista completa.

**Esenciales:**
- `SECRET_KEY`
- `DATABASE_URL` (proporcionada por Railway)
- `REDIS_URL` (proporcionada por Railway)
- `RESEND_API_KEY` (para emails)
- `CLOUDINARY_*` (para archivos media)

## Testing

```bash
# Ejecutar tests
python manage.py test apps.Autenticacion

# Test específico de OTP
python manage.py test apps.Autenticacion.test

# Coverage (requiere coverage.py)
coverage run --source='.' manage.py test
coverage report
```

## Notas Importantes

1. **Nunca commitear `.env`** al repositorio
2. **Usar variables de entorno** en Railway para todas las credenciales
3. **Habilitar SSL** automáticamente en Railway
4. **Configurar correctamente** `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS`
5. **Monitorear logs** en Railway dashboard para debugging

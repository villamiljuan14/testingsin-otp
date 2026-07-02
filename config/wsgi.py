"""
WSGI config for Enviart project.
Exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# 1. Detecta si estás en Railway/Render (Production) o en tu máquina local.
# Si la variable 'RAILWAY_ENVIRONMENT' o 'RENDER' existe en el servidor, usa production.py, si no, usa local.py
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

application = get_wsgi_application()
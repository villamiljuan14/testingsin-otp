#!/bin/bash
set -e

echo "=== Enviart startup ==="
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "PORT: $PORT"

echo ">>> Running migrations..."
python manage.py migrate --no-input

echo ">>> Starting Daphne on port $PORT..."
exec python -m daphne -b 0.0.0.0 -p "${PORT:-8000}" config.asgi:application

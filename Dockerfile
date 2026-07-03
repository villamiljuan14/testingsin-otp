FROM python:3.12-slim

# Variables de entorno base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.railway

WORKDIR /app

# Dependencias del sistema (psycopg2, Pillow, reportlab)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente
COPY . .

# Archivos estáticos (dummy SECRET_KEY solo para collectstatic)
RUN SECRET_KEY=build-only python manage.py collectstatic --no-input

EXPOSE 8000

CMD python -m daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application

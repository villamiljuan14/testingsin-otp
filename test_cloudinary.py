"""
Script de prueba de Cloudinary.
Ejecutar con: python test_cloudinary.py
"""
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

import cloudinary
import cloudinary.uploader
from django.conf import settings

cfg = settings.CLOUDINARY_STORAGE
print("=== Configuracion Cloudinary ===")
print("Cloud name :", cfg["CLOUD_NAME"])
print("API Key    :", cfg["API_KEY"])
print("Storage    :", settings.DEFAULT_FILE_STORAGE)
print()

# Imagen de prueba: 1x1 pixel PNG en base64
import base64
pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
pixel_bytes = base64.b64decode(pixel_b64)

print("Subiendo imagen de prueba a Cloudinary...")
try:
    result = cloudinary.uploader.upload(
        pixel_bytes,
        public_id="enviart_test/prueba_conexion",
        resource_type="image"
    )
    print()
    print("=== SUBIDA EXITOSA ===")
    print("URL publica :", result["secure_url"])
    print("Public ID   :", result["public_id"])
    print("Formato     :", result["format"])
    print("Tamano      :", result["bytes"], "bytes")
    print()
    print("Cloudinary esta funcionando correctamente!")
except Exception as e:
    print()
    print("=== ERROR AL SUBIR ===")
    print("Error:", e)
    sys.exit(1)

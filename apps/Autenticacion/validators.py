from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validar_telefono(value):
    """
    Valida formato de teléfono internacional.
    Limpia espacios y guiones comunes que los usuarios digitan en Flutter.
    """
    if not value:
        raise ValidationError(_('El teléfono es requerido.'))
        
    # Convertimos a string por seguridad y removemos espacios o guiones
    telefono_limpio = re.sub(r'[\s\-]', '', str(value))
    
    # Expresión regular que soporta código de país opcional (+) y entre 9 y 15 dígitos
    pattern = r'^\+?\d{9,15}$'
    if not re.match(pattern, telefono_limpio):
        raise ValidationError(_('Teléfono inválido. Debe tener entre 9 y 15 dígitos.'))


def validar_documento(value, tipo_documento):
    """
    Valida longitud mínima de documento según el tipo (CC, TI, NIT) de Colombia.
    Asegura que el valor se evalúe como texto limpio.
    """
    if not value or not tipo_documento:
        raise ValidationError(_('El tipo y número de documento son obligatorios.'))
        
    # Sanitizamos el valor: pasamos a string, quitamos espacios y dejamos en mayúsculas (por si trae letras como el NIT)
    doc_limpio = str(value).strip().upper()
    
    if tipo_documento == 'CC' and len(doc_limpio) < 7:
        raise ValidationError(_('La cédula debe tener al menos 7 dígitos.'))
        
    elif tipo_documento == 'TI' and len(doc_limpio) < 5:
        raise ValidationError(_('La tarjeta de identidad debe tener al menos 5 dígitos.'))
        
    elif tipo_documento == 'NIT' and len(doc_limpio) < 8:
        raise ValidationError(_('El NIT debe tener al menos 8 dígitos.'))
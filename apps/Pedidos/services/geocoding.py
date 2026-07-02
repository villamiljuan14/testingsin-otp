import requests
import time
import logging

logger = logging.getLogger(__name__)

def obtener_coordenadas(direccion, ciudad, departamento=None, pais="Colombia", defaults=None):
    """
    Obtiene latitud y longitud de una dirección mediante la API gratuita de Nominatim (OpenStreetMap).
    Para entornos de producción y uso intensivo, se debe usar una API de pago (Google Maps, Mapbox).
    Nominatim limita a 1 petición por segundo.
    
    Args:
        direccion (str): Línea de dirección (Ej. "Calle 123 #45-67")
        ciudad (str): Ciudad de destino.
        departamento (str, opcional): Departamento / Estado.
        pais (str): País por defecto.
        defaults (dict): Coordenadas de respaldo si falla (Lat/Lon).
        
    Returns:
        tuple: (latitud, longitud) o (None, None) / (defaults['lat'], defaults['lon'])
    """
    # Sleep to respect OpenStreetMap Nominatim Usage Policy (1 req/sec)
    time.sleep(1.1)
    
    # 1. Clean format (Removing `#` and `No` as Nominatim sometimes fails with them)
    direccion_limpia = direccion.replace("#", "").replace("No", "").strip() if direccion else ""

    # Construct the query string prioritizing the most specific fields first
    query_parts = []
    if direccion_limpia:
        query_parts.append(direccion_limpia)
    if ciudad:
        query_parts.append(ciudad)
    if departamento:
        query_parts.append(departamento)
    if pais:
        query_parts.append(pais)
        
    query = ", ".join(query_parts)
    
    headers = {
        'User-Agent': 'EnviartLogisticsSystem/1.0 (administracion@enviart.com)'
    }
    
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': query, 'format': 'json', 'limit': 1},
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
            
        # Fallback 1: Si no encuentra la dirección exacta, probamos solo la ciudad/departamento
        if direccion_limpia and ciudad:
            fallback_query = f"{ciudad}, {departamento}, {pais}" if departamento else f"{ciudad}, {pais}"
            logger.warning(f"Nominatim falló para '{query}'. Probando fallback: '{fallback_query}'")
            
            time.sleep(1.1)
            fb_response = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': fallback_query, 'format': 'json', 'limit': 1},
                headers=headers,
                timeout=5
            )
            fb_data = fb_response.json()
            if fb_data and len(fb_data) > 0:
                return float(fb_data[0]['lat']), float(fb_data[0]['lon'])
                
    except requests.RequestException as e:
        logger.error(f"Error de red al consultar Nominatim: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado en geocodificación: {str(e)}")

    # Fallback absolute: Retornar defaults si existen.
    if defaults:
        return defaults.get('lat'), defaults.get('lon')
        
    return None, None

from django.db import models


class TipoServicioEnvio(models.TextChoices):
    """Tipos de servicio tipo FedEx"""
    STANDARD = 'STANDARD', 'Envío Estándar (3-5 días)'
    EXPRESS = 'EXPRESS', 'Envío Express (1-2 días)'
    OVERNIGHT = 'OVERNIGHT', 'Envío Overnight (siguiente día)'
    SAME_DAY = 'SAME_DAY', 'Envío mismo día'
    INTERNATIONAL = 'INTERNATIONAL', 'Envío Internacional'
    ECONOMICO = 'ECONOMICO', 'Envío Económico (5-7 días)'


class EstadoPedido(models.TextChoices):
    """Estados del pedido - Ciclo completo"""
    BORRADOR = 'BORRADOR', 'Borrador'
    PENDIENTE_PAGO = 'PENDIENTE_PAGO', 'Pendiente de Pago'
    PAGO_FALLIDO = 'PAGO_FALLIDO', 'Pago Fallido'
    CONFIRMADO = 'CONFIRMADO', 'Confirmado'
    EN_PREPARACION = 'EN_PREPARACION', 'En preparación'
    RECOLECTADO = 'RECOLECTADO', 'Recolectado'
    EN_HUB_ORIGEN = 'EN_HUB_ORIGEN', 'En hub de origen'
    EN_TRANSITO = 'EN_TRANSITO', 'En tránsito'
    EN_HUB_DESTINO = 'EN_HUB_DESTINO', 'En hub de destino'
    EN_REPARTO = 'EN_REPARTO', 'En reparto'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    INTENTO_FALLIDO = 'INTENTO_FALLIDO', 'Intento fallido'
    DEVUELTO = 'DEVUELTO', 'Devuelto'
    CANCELADO = 'CANCELADO', 'Cancelado'


class EstadoGuia(models.TextChoices):
    """Estados de la guía de envío"""
    GENERADA = 'GENERADA', 'Generada'
    IMPRESA = 'IMPRESA', 'Impresa'
    EN_CIRCULACION = 'EN_CIRCULACION', 'En circulación'
    CERRADA = 'CERRADA', 'Cerrada'
    ANULADA = 'ANULADA', 'Anulada'


class TipoEventoTracking(models.TextChoices):
    """Eventos de tracking granulares tipo FedEx"""
    GUIA_CREADA = 'GUIA_CREADA', 'Guía creada'
    PEDIDO_CONFIRMADO = 'PEDIDO_CONFIRMADO', 'Pedido confirmado'
    RECOLECTADO = 'RECOLECTADO', 'Recolectado por mensajero'
    LLEGADA_HUB_ORIGEN = 'LLEGADA_HUB_ORIGEN', 'Llegada a hub de origen'
    SALIDA_HUB_ORIGEN = 'SALIDA_HUB_ORIGEN', 'Salida de hub de origen'
    EN_TRANSITO = 'EN_TRANSITO', 'En tránsito'
    LLEGADA_HUB_DESTINO = 'LLEGADA_HUB_DESTINO', 'Llegada a hub de destino'
    SALIDA_HUB_DESTINO = 'SALIDA_HUB_DESTINO', 'Salida de hub de destino'
    EN_REPARTO = 'EN_REPARTO', 'En reparto'
    INTENTO_ENTREGA = 'INTENTO_ENTREGA', 'Intento de entrega'
    ENTREGADO = 'ENTREGADO', 'Entregado'
    NO_CONTESTA = 'NO_CONTESTA', 'Destinatario no contesta'
    DIRECCION_INCORRECTA = 'DIRECCION_INCORRECTA', 'Dirección incorrecta'
    DEVUELTO_REMITENTE = 'DEVUELTO_REMITENTE', 'Devuelto al remitente'
    CANCELADO = 'CANCELADO', 'Cancelado'


class TipoReclamo(models.TextChoices):
    """Tipos de reclamos"""
    RETRASO = 'RETRASO', 'Retraso en entrega'
    DAÑO = 'DAÑO', 'Paquete dañado'
    EXTRAVIO = 'EXTRAVIO', 'Paquete extraviado'
    ENTREGA_INCORRECTA = 'ENTREGA_INCORRECTA', 'Entrega incorrecta'
    COBRANZA_INDEBIDA = 'COBRANZA_INDEBIDA', 'Cobranza indebida'
    OTRO = 'OTRO', 'Otro'


class PrioridadReclamo(models.TextChoices):
    BAJO = 'BAJO', 'Bajo'
    MEDIO = 'MEDIO', 'Medio'
    ALTO = 'ALTO', 'Alto'
    CRITICO = 'CRITICO', 'Crítico'


class TipoNotificacion(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push Notification'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
from django.db import models


class TipoNovedad(models.TextChoices):
    """Tipos de novedades - Expandido para cubrir todos los casos"""
    ACTUALIZACION = 'ACTUALIZACION', 'Actualización de Estado'
    INCIDENCIA = 'INCIDENCIA', 'Incidencia Operativa'
    ENTREGA = 'ENTREGA', 'Incidencia en Entrega'
    VEHICULO = 'VEHICULO', 'Incidencia con Vehículo'
    CONDUCTOR = 'CONDUCTOR', 'Incidencia con Conductor'
    CLIENTE = 'CLIENTE', 'Reclamo de Cliente'
    SEGURIDAD = 'SEGURIDAD', 'Incidente de Seguridad'
    CALIDAD = 'CALIDAD', 'Problema de Calidad'
    RETRASO = 'RETRASO', 'Retraso en Entrega'
    DAÑO = 'DAÑO', 'Paquete Dañado'
    EXTRAVIO = 'EXTRAVIO', 'Paquete Extraviado'
    DIRECCION = 'DIRECCION', 'Dirección Incorrecta'
    CLIMA = 'CLIMA', 'Condiciones Climáticas'
    TECNOLOGIA = 'TECNOLOGIA', 'Falla Tecnológica'
    OTRO = 'OTRO', 'Otro'


class SeveridadNovedad(models.TextChoices):
    """Niveles de severidad para priorización"""
    BAJO = 'BAJO', 'Bajo - Sin impacto operativo'
    MEDIO = 'MEDIO', 'Medio - Impacto menor'
    ALTO = 'ALTO', 'Alto - Impacto significativo'
    CRITICO = 'CRITICO', 'Crítico - Impacto severo'
    EMERGENCIA = 'EMERGENCIA', 'Emergencia - Requiere acción inmediata'


class EstadoNovedad(models.TextChoices):
    """Estados del ciclo de vida de la novedad"""
    REGISTRADA = 'REGISTRADA', 'Registrada'
    EN_REVISION = 'EN_REVISION', 'En Revisión'
    ASIGNADA = 'ASIGNADA', 'Asignada'
    EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
    EN_ESPERA = 'EN_ESPERA', 'En Espera de Información'
    RESUELTA = 'RESUELTA', 'Resuelta'
    CERRADA = 'CERRADA', 'Cerrada'
    REABIERTA = 'REABIERTA', 'Reabierta'
    ESCALADA = 'ESCALADA', 'Escalada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class TipoAccion(models.TextChoices):
    """Tipos de acciones correctivas"""
    INMEDIATA = 'INMEDIATA', 'Acción Inmediata'
    CORRECTIVA = 'CORRECTIVA', 'Acción Correctiva'
    PREVENTIVA = 'PREVENTIVA', 'Acción Preventiva'
    MITIGACION = 'MITIGACION', 'Mitigación de Impacto'
    INVESTIGACION = 'INVESTIGACION', 'Investigación'
    COMPENSACION = 'COMPENSACION', 'Compensación al Cliente'
    OTRO = 'OTRO', 'Otra'


class TipoEvidencia(models.TextChoices):
    """Tipos de evidencia adjunta"""
    FOTO = 'FOTO', 'Fotografía'
    VIDEO = 'VIDEO', 'Video'
    DOCUMENTO = 'DOCUMENTO', 'Documento'
    AUDIO = 'AUDIO', 'Audio'
    CAPTURA = 'CAPTURA', 'Captura de Pantalla'
    FIRMA = 'FIRMA', 'Firma Digital'
    OTRO = 'OTRO', 'Otro'


class MotivoEscalamiento(models.TextChoices):
    """Motivos para escalar una novedad"""
    TIEMPO_AGOTADO = 'TIEMPO_AGOTADO', 'Tiempo de SLA agotado'
    SEVERIDAD_ALTA = 'SEVERIDAD_ALTA', 'Severidad requiere atención superior'
    SIN_RESPUESTA = 'SIN_RESPUESTA', 'Sin respuesta del asignado'
    REQUERIMIENTO_ESPECIAL = 'REQUERIMIENTO_ESPECIAL', 'Requiere autorización especial'
    REPETICION = 'REPETICION', 'Novedad recurrente'
    IMPACTO_AMPLIO = 'IMPACTO_AMPLIO', 'Impacto en múltiples áreas'
    SOLICITUD_CLIENTE = 'SOLICITUD_CLIENTE', 'Solicitud del cliente'
    OTRO = 'OTRO', 'Otro'
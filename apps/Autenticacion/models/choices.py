from django.db import models


class TipoRol(models.TextChoices):
    # Ajustado el valor a 'ADMINISTRADOR' para sintonizar con Usuario.es_admin()
    ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
    MENSAJERO = 'MENSAJERO', 'Mensajero'
    CLIENTE = 'CLIENTE', 'Cliente'
    PROVEEDOR = 'PROVEEDOR', 'Proveedor'


class TipoDocumento(models.TextChoices):
    CC = 'CC', 'Cédula de Ciudadanía'
    TI = 'TI', 'Tarjeta de Identidad'
    CE = 'CE', 'Cédula de Extranjería'
    PP = 'PP', 'Pasaporte'
    NIT = 'NIT', 'Número de Identificación Tributaria (NIT)'


class EstadoUsuario(models.TextChoices):
    ACTIVO = 'ACTIVO', 'Activo'
    INACTIVO = 'INACTIVO', 'Inactivo'
    BLOQUEADO = 'BLOQUEADO', 'Bloqueado'
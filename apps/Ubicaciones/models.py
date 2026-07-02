from django.db import models
from django.core.validators import RegexValidator


class Pais(models.Model):
    """
    Modelo de Países - Sistema normalizado de ubicaciones
    Basado en estándares ISO 3166-1
    """
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        validators=[RegexValidator(r'^[A-Za-z\s]+$', 'Solo letras permitidas')]
    )
    codigo_iso = models.CharField(
        max_length=2, 
        unique=True,
        help_text='Código ISO 3166-1 alpha-2'
    )
    codigo_iso3 = models.CharField(
        max_length=3, 
        unique=True,
        null=True, 
        blank=True,
        help_text='Código ISO 3166-1 alpha-3'
    )
    codigo_telefonico = models.CharField(
        max_length=5,
        help_text='Código de teléfono internacional'
    )
    moneda = models.CharField(
        max_length=3,
        help_text='Código de moneda ISO 4217'
    )
    idioma_principal = models.CharField(
        max_length=2,
        help_text='Código de idioma principal ISO 639-1'
    )
    zona_horaria = models.CharField(
        max_length=50,
        null=True, 
        blank=True
    )
    es_activo = models.BooleanField(
        default=True,
        help_text='País disponible para envíos'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paises'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_iso']),
            models.Index(fields=['nombre']),
            models.Index(fields=['es_activo']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.codigo_iso})'

    @property
    def nombre_completo(self):
        """Retorna nombre con código ISO"""
        return f'{self.nombre} - {self.codigo_iso}'


class Departamento(models.Model):
    """
    Modelo de Departamentos/Estados - Primera división administrativa
    """
    nombre = models.CharField(
        max_length=100,
        validators=[RegexValidator(r'^[A-Za-z\s\-\']+$', 'Solo letras, guiones y apóstrofes')]
    )
    codigo_dane = models.CharField(
        max_length=5,
        unique=True,
        help_text='Código DANE (Colombia) o equivalente'
    )
    pais = models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name='departamentos'
    )
    codigo_divipola = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        help_text='Código DIVIPOLA'
    )
    region = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departamentos'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']
        unique_together = [['nombre', 'pais']]
        indexes = [
            models.Index(fields=['pais', 'nombre']),
            models.Index(fields=['codigo_dane']),
            models.Index(fields=['es_activo']),
        ]

    def __str__(self):
        return f'{self.nombre}, {self.pais.nombre}'


class Ciudad(models.Model):
    """
    Modelo de Ciudades - Segunda división administrativa
    Incluye coordenadas para geolocalización
    """
    nombre = models.CharField(
        max_length=100,
        validators=[RegexValidator(r'^[A-Za-z\s\-\']+$', 'Solo letras, guiones y apóstrofes')]
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='ciudades'
    )
    codigo_postal = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='Código postal'
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Latitud para geolocalización'
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Longitud para geolocalización'
    )
    altitud = models.FloatField(
        null=True,
        blank=True,
        help_text='Altitud sobre el nivel del mar (metros)'
    )
    zona_postal = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    area_urbana = models.BooleanField(
        default=True,
        help_text='Ciudad considera área urbana'
    )
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ciudades'
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
        ordering = ['nombre']
        unique_together = [['nombre', 'departamento']]
        indexes = [
            models.Index(fields=['departamento', 'nombre']),
            models.Index(fields=['codigo_postal']),
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['es_activo']),
        ]

    def __str__(self):
        return f'{self.nombre}, {self.departamento.nombre}'

    @property
    def nombre_completo(self):
        """Retorna nombre completo con departamento y país"""
        return f'{self.nombre}, {self.departamento.nombre}, {self.departamento.pais.nombre}'

    @property
    def coordenadas(self):
        """Retorna coordenadas formateadas"""
        if self.latitud and self.longitud:
            return f'{self.latitud}, {self.longitud}'
        return None


class Hub(models.Model):
    """
    Modelo de Hubs/Puntos de Distribución
    Centros logísticos del sistema
    """
    TIPO_HUB_CHOICES = [
        ('PRINCIPAL', 'Hub Principal'),
        ('SECUNDARIO', 'Hub Secundario'),
        ('TEMPORAL', 'Hub Temporal'),
        ('PARTNER', 'Hub de Partner'),
    ]

    nombre = models.CharField(
        max_length=100,
        unique=True
    )
    codigo_hub = models.CharField(
        max_length=10,
        unique=True,
        help_text='Código único del hub'
    )
    tipo_hub = models.CharField(
        max_length=20,
        choices=TIPO_HUB_CHOICES,
        default='PRINCIPAL'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        related_name='hubs'
    )
    direccion = models.CharField(
        max_length=200,
        help_text='Dirección completa del hub'
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    email_contacto = models.EmailField(
        null=True,
        blank=True
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    capacidad_operativa = models.PositiveIntegerField(
        default=1000,
        help_text='Capacidad operativa diaria (paquetes)'
    )
    horario_operacion = models.CharField(
        max_length=100,
        default='08:00-18:00',
        help_text='Horario de operación'
    )
    servicios_disponibles = models.JSONField(
        default=dict,
        help_text='Servicios disponibles en el hub'
    )
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hubs'
        verbose_name = 'Hub'
        verbose_name_plural = 'Hubs'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_hub']),
            models.Index(fields=['ciudad']),
            models.Index(fields=['tipo_hub']),
            models.Index(fields=['es_activo']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.codigo_hub})'

    @property
    def direccion_completa(self):
        """Retorna dirección completa con ciudad"""
        if self.ciudad:
            return f'{self.direccion}, {self.ciudad.nombre}'
        return self.direccion

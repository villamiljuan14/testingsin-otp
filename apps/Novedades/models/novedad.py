from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from .choices import (
    TipoNovedad, SeveridadNovedad, EstadoNovedad, MotivoEscalamiento
)
from .categoria import CategoriaNovedad


class Novedad(models.Model):
    """
    Novedad/Incidencia - Entidad principal del módulo.
    Gestiona todo tipo de incidentes operativos.
    Normalizada a 4NF con entidades separadas para evidencias, acciones, etc.
    """
    # ✅ Identificación única
    codigo_novedad = models.CharField(max_length=50, unique=True, db_index=True, editable=False)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # ✅ Clasificación
    tipo = models.CharField(
        max_length=30,
        choices=TipoNovedad.choices,
        db_index=True
    )
    categoria = models.ForeignKey(
        CategoriaNovedad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades'
    )
    severidad = models.CharField(
        max_length=20,
        choices=SeveridadNovedad.choices,
        default=SeveridadNovedad.MEDIO,
        db_index=True
    )
    prioridad = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MinValueValidator(5)],
        help_text='1=Máxima prioridad, 5=Mínima prioridad'
    )
    
    # ✅ Estado
    estado = models.CharField(
        max_length=30,
        choices=EstadoNovedad.choices,
        default=EstadoNovedad.REGISTRADA,
        db_index=True
    )
    
    # ✅ Entidades relacionadas (polimórfico simplificado)
    pedido = models.ForeignKey(
        'Pedidos.Pedido',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='novedades'
    )
    ruta = models.ForeignKey(
        'Rutas.Ruta',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='novedades'
    )
    vehiculo = models.ForeignKey(
        'Vehiculos.Vehiculo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='novedades'
    )
    conductor = models.ForeignKey(
        'Vehiculos.Conductor',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='novedades'
    )
    
    # ✅ Ubicación del incidente
    ubicacion_texto = models.TextField(null=True, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # ✅ Fechas y SLA
    fecha_registro = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_limite_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_limite_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    # ✅ Asignación
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='novedades_registradas'
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_asignadas'
    )
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_asignadas_por'
    )
    
    # ✅ Escalamiento
    esta_escalada = models.BooleanField(default=False)
    nivel_escalamiento = models.PositiveIntegerField(default=0)
    fecha_ultimo_escalamiento = models.DateTimeField(null=True, blank=True)
    motivo_ultimo_escalamiento = models.CharField(
        max_length=50,
        choices=MotivoEscalamiento.choices,
        null=True,
        blank=True
    )
    escalada_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='novedades_escaladas_a'
    )
    
    # ✅ Impacto
    impacto_economico = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    impacto_operativo = models.TextField(null=True, blank=True)
    clientes_afectados = models.PositiveIntegerField(default=0)
    
    # ✅ Resolución
    causa_raiz = models.TextField(null=True, blank=True)
    solucion_aplicada = models.TextField(null=True, blank=True)
    lecciones_aprendidas = models.TextField(null=True, blank=True)
    
    # ✅ SLA
    sla_cumplido = models.BooleanField(null=True, blank=True)
    tiempo_respuesta_horas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tiempo_resolucion_horas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # ✅ Auditoría
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'novedades_novedad'
        verbose_name = 'Novedad'
        verbose_name_plural = 'Novedades'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['codigo_novedad']),
            models.Index(fields=['estado', 'severidad']),
            models.Index(fields=['fecha_registro', 'estado']),
            models.Index(fields=['asignado_a', 'estado']),
            models.Index(fields=['pedido', 'fecha_registro']),
            models.Index(fields=['ruta', 'fecha_registro']),
            models.Index(fields=['esta_escalada', 'severidad']),
        ]
    
    def __str__(self):
        return f'{self.codigo_novedad} - {self.titulo}'
    
    def save(self, *args, **kwargs):
        """Genera código de novedad automático"""
        if not self.codigo_novedad:
            from django.utils import timezone
            year = timezone.now().year
            last_novedad = Novedad.objects.filter(
                codigo_novedad__startswith=f'NOV-{year}-'
            ).order_by('-codigo_novedad').first()
            
            if last_novedad:
                last_num = int(last_novedad.codigo_novedad.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.codigo_novedad = f'NOV-{year}-{new_num:06d}'
        
        # ✅ Calcular SLA si es nueva
        if not self.fecha_limite_respuesta and self.categoria:
            from django.utils import timezone
            from datetime import timedelta
            self.fecha_limite_respuesta = timezone.now() + timedelta(
                hours=self.categoria.sla_horas_respuesta
            )
            self.fecha_limite_resolucion = timezone.now() + timedelta(
                hours=self.categoria.sla_horas_resolucion
            )
        
        super().save(*args, **kwargs)
    
    @property
    def tiempo_transcurrido_horas(self):
        """Calcula horas transcurridas desde el registro"""
        from django.utils import timezone
        delta = timezone.now() - self.fecha_registro
        return round(delta.total_seconds() / 3600, 2)
    
    @property
    def sla_vencido(self):
        """Verifica si el SLA está vencido"""
        from django.utils import timezone
        if self.fecha_limite_resolucion:
            return timezone.now() > self.fecha_limite_resolucion
        return False
    
    @property
    def respuesta_pendiente(self):
        """Verifica si la respuesta está pendiente"""
        return self.estado in [EstadoNovedad.REGISTRADA, EstadoNovedad.EN_REVISION]
    
    def puede_asignar(self, usuario):
        """Verifica si el usuario puede asignar la novedad"""
        return usuario.es_admin() or usuario.rol and usuario.rol.tipo_rol in ['ADMIN', 'FLEET_MANAGER']
    
    def puede_resolver(self, usuario):
        """Verifica si el usuario puede resolver la novedad"""
        return (
            usuario.es_admin() or
            self.asignado_a == usuario or
            (self.registrado_por == usuario and self.estado == EstadoNovedad.REGISTRADA)
        )
    
    def asignar(self, usuario_asignado, usuario_asigna):
        """Asigna la novedad a un usuario"""
        from django.utils import timezone
        if not self.puede_asignar(usuario_asigna):
            raise ValueError('No tienes permisos para asignar esta novedad')
        
        self.asignado_a = usuario_asignado
        self.fecha_asignacion = timezone.now()
        self.asignado_por = usuario_asigna
        self.estado = EstadoNovedad.ASIGNADA
        self.save()
        
        # ✅ Crear registro de seguimiento
        from .seguimiento import SeguimientoNovedad
        SeguimientoNovedad.objects.create(
            novedad=self,
            campo_cambiado='asignacion',
            valor_anterior=None,
            valor_nuevo=usuario_asignado.email,
            usuario=usuario_asigna
        )
    
    def actualizar_estado(self, nuevo_estado, usuario):
        """Actualiza el estado de la novedad"""
        estados_validos = [choice[0] for choice in EstadoNovedad.choices]
        if nuevo_estado not in estados_validos:
            raise ValueError(f'Estado inválido. Opciones: {estados_validos}')
        
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save()
        
        # ✅ Registrar en seguimiento
        from .seguimiento import SeguimientoNovedad
        SeguimientoNovedad.objects.create(
            novedad=self,
            campo_cambiado='estado',
            valor_anterior=estado_anterior,
            valor_nuevo=nuevo_estado,
            usuario=usuario
        )
        
        # ✅ Actualizar fechas según estado
        from django.utils import timezone
        if nuevo_estado == EstadoNovedad.RESUELTA and not self.fecha_resolucion:
            self.fecha_resolucion = timezone.now()
            self.tiempo_resolucion_horas = self.tiempo_transcurrido_horas
            self.sla_cumplido = not self.sla_vencido
            self.save()
    
    def escalar(self, usuario_destino, motivo, usuario_escala):
        """Escala la novedad a otro nivel"""
        from django.utils import timezone
        self.esta_escalada = True
        self.nivel_escalamiento += 1
        self.fecha_ultimo_escalamiento = timezone.now()
        self.motivo_ultimo_escalamiento = motivo
        self.escalada_a = usuario_destino
        self.estado = EstadoNovedad.ESCALADA
        self.save()
        
        # ✅ Registrar en seguimiento
        from .seguimiento import SeguimientoNovedad
        SeguimientoNovedad.objects.create(
            novedad=self,
            campo_cambiado='escalamiento',
            valor_anterior=f'Nivel {self.nivel_escalamiento - 1}',
            valor_nuevo=f'Nivel {self.nivel_escalamiento}',
            usuario=usuario_escala,
            observaciones=motivo
        )
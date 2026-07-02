from django.db import models, transaction
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from .choices import EstadoPedido, TipoServicioEnvio
from .hub import Hub
from .servicio import TipoServicio


class Pedido(models.Model):
    numero_pedido = models.CharField(max_length=50,unique=True,db_index=True,editable=False)
    codigo_rastreo = models.CharField(max_length=50,unique=True,db_index=True,editable=False,help_text='Código para tracking público')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='pedidos_modernos',help_text='Cliente que solicita el envío')
    pais_origen = models.ForeignKey('Ubicaciones.Pais',on_delete=models.PROTECT,related_name='pedidos_origen',null=True,blank=True,help_text='País de origen del envío')
    departamento_origen = models.ForeignKey('Ubicaciones.Departamento',on_delete=models.PROTECT,related_name='pedidos_origen',null=True,blank=True,help_text='Departamento/Estado de origen')
    ciudad_origen = models.ForeignKey('Ubicaciones.Ciudad',on_delete=models.PROTECT,related_name='pedidos_origen',null=True,blank=True,help_text='Ciudad de origen')
    pais_destino = models.ForeignKey('Ubicaciones.Pais',on_delete=models.PROTECT,related_name='pedidos_destino',null=True,blank=True,help_text='País de destino del envío')
    departamento_destino = models.ForeignKey('Ubicaciones.Departamento',on_delete=models.PROTECT,related_name='pedidos_destino',null=True,blank=True,help_text='Departamento/Estado de destino')
    ciudad_destino = models.ForeignKey('Ubicaciones.Ciudad',on_delete=models.PROTECT,related_name='pedidos_destino',null=True,blank=True,help_text='Ciudad de destino')
    
    direccion_origen_calle = models.CharField(max_length=200,null=True,blank=True,help_text='Calle/Avenida de origen')
    direccion_origen_numero = models.CharField(max_length=20,null=True,blank=True,help_text='Número de puerta/edificio')
    direccion_origen_barrio = models.CharField(max_length=100,null=True,blank=True,help_text='Barrio/Colonia')
    direccion_origen_referencia = models.TextField(null=True,blank=True,help_text='Referencias adicionales para encontrar el lugar')
    
    direccion_destino_calle = models.CharField(max_length=200,null=True,blank=True,help_text='Calle/Avenida de destino')
    direccion_destino_numero = models.CharField(max_length=20,null=True,blank=True,help_text='Número de puerta/edificio')
    direccion_destino_barrio = models.CharField(max_length=100,null=True,blank=True,help_text='Barrio/Colonia')
    direccion_destino_referencia = models.TextField(null=True,blank=True,help_text='Referencias adicionales para encontrar el lugar')

    direccion_origen_texto = models.TextField(help_text='Copia de dirección completa de origen al momento del pedido',editable=False)
    direccion_destino_texto = models.TextField(help_text='Copia de dirección completa de destino al momento del pedido',editable=False)
    
    latitud_destino = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,help_text='Latitud exacta generada por Geocoding')
    longitud_destino = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,help_text='Longitud exacta generada por Geocoding')

    nombre_destinatario = models.CharField(max_length=100)
    telefono_destinatario = models.CharField(max_length=20)
    email_destinatario = models.EmailField(null=True, blank=True)
    
    tipo_servicio = models.ForeignKey(TipoServicio,on_delete=models.PROTECT,related_name='pedidos')
    
    hub_origen = models.ForeignKey(Hub,on_delete=models.SET_NULL,null=True,blank=True,related_name='pedidos_origen',help_text='Hub donde inicia el envío')
    hub_destino = models.ForeignKey(Hub,on_delete=models.SET_NULL,null=True,blank=True,related_name='pedidos_destino',help_text='Hub de destino final')
    
    peso_real_kg = models.DecimalField(max_digits=8,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
    peso_volumetrico_kg = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True,help_text='Peso calculado por dimensiones (largo*ancho*alto/5000)')
    largo_cm = models.PositiveIntegerField(null=True, blank=True)
    ancho_cm = models.PositiveIntegerField(null=True, blank=True)
    alto_cm = models.PositiveIntegerField(null=True, blank=True)
    
    descripcion_contenido = models.CharField(max_length=255,help_text='Descripción breve del contenido')
    valor_declarado = models.DecimalField(max_digits=12,decimal_places=2,default=Decimal('0.00'),help_text='Valor del contenido para seguro')
    es_fragil = models.BooleanField(default=False)
    requiere_firma = models.BooleanField(default=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_final = models.DecimalField(max_digits=10, decimal_places=2)
    
    estado = models.CharField(max_length=30,choices=EstadoPedido.choices,default=EstadoPedido.BORRADOR)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_estimada_entrega = models.DateTimeField(null=True, blank=True)
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    mensajero = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='pedidos_asignados',limit_choices_to={'rol__tipo_rol': 'MENSAJERO'})
    instrucciones_entrega = models.TextField(null=True,blank=True,help_text='Instrucciones especiales para la entrega')
    notas_internas = models.TextField(null=True,blank=True,help_text='Solo visible para staff')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pedidos_pedido'
        verbose_name = 'Pedido de Envío'
        verbose_name_plural = 'Pedidos de Envío'
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['codigo_rastreo']),
            models.Index(fields=['usuario', 'fecha_pedido']),
            models.Index(fields=['estado', 'fecha_pedido']),
            models.Index(fields=['hub_origen', 'estado']),
            models.Index(fields=['hub_destino', 'estado']),
            models.Index(fields=['mensajero', 'estado']),
            models.Index(fields=['ciudad_origen', 'estado']),
            models.Index(fields=['ciudad_destino', 'estado']),
            models.Index(fields=['departamento_origen', 'estado']),
            models.Index(fields=['departamento_destino', 'estado']),
            models.Index(fields=['pais_origen', 'pais_destino']),
        ]
    
    def __str__(self):
        return f'{self.numero_pedido} - {self.nombre_destinatario}'
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            from django.utils import timezone
            year = timezone.now().year
            # Usar select_for_update dentro de una transacción atómica para evitar
            # condiciones de carrera cuando dos requests llegan simultáneamente
            with transaction.atomic():
                last_pedido = Pedido.objects.select_for_update().filter(
                    numero_pedido__startswith=f'PED-{year}-'
                ).order_by('-id').first()  # Orden por ID numérico, no por texto
                
                if last_pedido:
                    last_num = int(last_pedido.numero_pedido.split('-')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                self.numero_pedido = f'PED-{year}-{new_num:06d}'
        if not self.codigo_rastreo:
            import secrets
            self.codigo_rastreo = f'ENV{secrets.token_hex(8).upper()}'
        if self.largo_cm and self.ancho_cm and self.alto_cm:
            self.peso_volumetrico_kg = Decimal(
                (self.largo_cm * self.ancho_cm * self.alto_cm) / 5000
            ).quantize(Decimal('0.01'))
        
        self._guardar_snapshots_ubicaciones()

        if not self.fecha_estimada_entrega and self.tipo_servicio:
            self.calcular_fecha_estimada()
        if not self.latitud_destino or not self.longitud_destino:
            if self.ciudad_destino:
                from apps.Pedidos.services.geocoding import obtener_coordenadas
                
                dir_str = self.direccion_destino_calle or ""
                    
                depto_nombre = self.departamento_destino.nombre if self.departamento_destino else None
                pais_nombre = self.pais_destino.nombre if self.pais_destino else "Colombia"
                
                fallback_coords = {}
                if self.ciudad_destino and self.ciudad_destino.latitud and self.ciudad_destino.longitud:
                    fallback_coords = {'lat': self.ciudad_destino.latitud, 'lon': self.ciudad_destino.longitud}
                    
                lat, lon = obtener_coordenadas(
                    direccion=dir_str,
                    ciudad=self.ciudad_destino.nombre,
                    departamento=depto_nombre,
                    pais=pais_nombre,
                    defaults=fallback_coords
                )
                
                self.latitud_destino = lat
                self.longitud_destino = lon
        
        super().save(*args, **kwargs)
    
    def _guardar_snapshots_ubicaciones(self):
        partes_origen = []
        
        if self.direccion_origen_calle:
            calle_numero = self.direccion_origen_calle
            if self.direccion_origen_numero:
                calle_numero += f' #{self.direccion_origen_numero}'
            partes_origen.append(calle_numero)
        
        if self.direccion_origen_barrio:
            partes_origen.append(self.direccion_origen_barrio)
        
        if self.ciudad_origen:
            ubicacion = f'{self.ciudad_origen.nombre}, {self.ciudad_origen.departamento.nombre}, {self.ciudad_origen.departamento.pais.nombre}'
            partes_origen.append(ubicacion)
        elif self.departamento_origen:
            ubicacion = f'{self.departamento_origen.nombre}, {self.departamento_origen.pais.nombre}'
            partes_origen.append(ubicacion)
        elif self.pais_origen:
            partes_origen.append(self.pais_origen.nombre)
        
        if partes_origen:
            self.direccion_origen_texto = ' - '.join(partes_origen)
        
        partes_destino = []
        
        if self.direccion_destino_calle:
            calle_numero = self.direccion_destino_calle
            if self.direccion_destino_numero:
                calle_numero += f' #{self.direccion_destino_numero}'
            partes_destino.append(calle_numero)
        
        if self.direccion_destino_barrio:
            partes_destino.append(self.direccion_destino_barrio)
        
        # Ubicación jerárquica
        if self.ciudad_destino:
            ubicacion = f'{self.ciudad_destino.nombre}, {self.ciudad_destino.departamento.nombre}, {self.ciudad_destino.departamento.pais.nombre}'
            partes_destino.append(ubicacion)
        elif self.departamento_destino:
            ubicacion = f'{self.departamento_destino.nombre}, {self.departamento_destino.pais.nombre}'
            partes_destino.append(ubicacion)
        elif self.pais_destino:
            partes_destino.append(self.pais_destino.nombre)
        
        if partes_destino:
            self.direccion_destino_texto = ' - '.join(partes_destino)
    
    @property
    def peso_cobrar(self):
        if self.peso_volumetrico_kg:
            return max(self.peso_real_kg, self.peso_volumetrico_kg)
        return self.peso_real_kg
    
    @property
    def esta_entregado(self):
        return self.estado == EstadoPedido.ENTREGADO
    
    @property
    def esta_en_transito(self):
        return self.estado in [
            EstadoPedido.EN_TRANSITO,
            EstadoPedido.EN_REPARTO,
            EstadoPedido.EN_HUB_DESTINO
        ]
    
    @property
    def origen_completo(self):
        if self.ciudad_origen:
            return self.ciudad_origen.nombre_completo
        elif self.departamento_origen:
            return f'{self.departamento_origen.nombre}, {self.departamento_origen.pais.nombre}'
        elif self.pais_origen:
            return self.pais_origen.nombre
        return self.direccion_origen_texto or 'Ubicación no especificada'
    
    @property
    def destino_completo(self):
        if self.ciudad_destino:
            return self.ciudad_destino.nombre_completo
        elif self.departamento_destino:
            return f'{self.departamento_destino.nombre}, {self.departamento_destino.pais.nombre}'
        elif self.pais_destino:
            return self.pais_destino.nombre
        return self.direccion_destino_texto or 'Ubicación no especificada'
    
    @property
    def es_internacional(self):
        """Verifica si el envío es internacional"""
        if self.pais_origen and self.pais_destino:
            return self.pais_origen != self.pais_destino
        return False
    
    def puede_cancelar(self, usuario):
        """Verifica si el pedido puede ser cancelado"""
        if usuario.es_admin():
            return True
        if self.usuario != usuario:
            return False
        return self.estado in [
            EstadoPedido.BORRADOR,
            EstadoPedido.PENDIENTE_PAGO,
            EstadoPedido.PAGO_FALLIDO,
            EstadoPedido.CONFIRMADO
        ]
    
    def calcular_fecha_estimada(self):
        """Calcula fecha estimada de entrega basada en el servicio"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.tipo_servicio:
            dias = self.tipo_servicio.dias_entrega_max
            self.fecha_estimada_entrega = timezone.now() + timedelta(days=dias)
            return self.fecha_estimada_entrega
        return None
    
    def calcular_distancia_km(self):
        from math import radians, cos, sin, asin, sqrt
        
        if not (self.ciudad_origen and self.ciudad_destino):
            return None
        
        if not (self.ciudad_origen.latitud and self.ciudad_destino.latitud):
            return None
        
        def haversine(lat1, lon1, lat2, lon2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            return km
        
        return haversine(
            float(self.ciudad_origen.latitud),
            float(self.ciudad_origen.longitud),
            float(self.ciudad_destino.latitud),
            float(self.ciudad_destino.longitud)
        )
    
    def actualizar_estado(self, nuevo_estado, usuario=None):
        """
        Actualiza el estado del pedido con validación de transiciones.
        """
        transiciones_validas = {
            EstadoPedido.BORRADOR: [EstadoPedido.PENDIENTE_PAGO, EstadoPedido.CONFIRMADO, EstadoPedido.CANCELADO],
            EstadoPedido.PENDIENTE_PAGO: [EstadoPedido.CONFIRMADO, EstadoPedido.PAGO_FALLIDO, EstadoPedido.CANCELADO],
            EstadoPedido.PAGO_FALLIDO: [EstadoPedido.PENDIENTE_PAGO, EstadoPedido.CANCELADO],
            EstadoPedido.CONFIRMADO: [EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO],
            EstadoPedido.EN_PREPARACION: [EstadoPedido.RECOLECTADO],
            EstadoPedido.RECOLECTADO: [EstadoPedido.EN_HUB_ORIGEN],
            EstadoPedido.EN_HUB_ORIGEN: [EstadoPedido.EN_TRANSITO],
            EstadoPedido.EN_TRANSITO: [EstadoPedido.EN_HUB_DESTINO],
            EstadoPedido.EN_HUB_DESTINO: [EstadoPedido.EN_REPARTO],
            EstadoPedido.EN_REPARTO: [EstadoPedido.ENTREGADO, EstadoPedido.INTENTO_FALLIDO],
            EstadoPedido.INTENTO_FALLIDO: [EstadoPedido.EN_REPARTO, EstadoPedido.DEVUELTO],
        }
        
        if self.estado not in transiciones_validas:
            raise ValueError(f'Estado actual ({self.estado}) no permite transiciones')
        
        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            raise ValueError(
                f'No se puede cambiar de {self.estado} a {nuevo_estado}'
            )
        
        self.estado = nuevo_estado
        self.save(update_fields=['estado', 'actualizado_en'])
        
        # ✅ Crear evento de tracking automáticamente
        if usuario:
            from .tracking import EventoTracking
            from .choices import TipoEventoTracking
            
            evento_mapping = {
                EstadoPedido.CONFIRMADO: TipoEventoTracking.PEDIDO_CONFIRMADO,
                EstadoPedido.EN_PREPARACION: TipoEventoTracking.RECOLECTADO,
                EstadoPedido.EN_HUB_ORIGEN: TipoEventoTracking.LLEGADA_HUB_ORIGEN,
                EstadoPedido.EN_TRANSITO: TipoEventoTracking.EN_TRANSITO,
                EstadoPedido.EN_HUB_DESTINO: TipoEventoTracking.LLEGADA_HUB_DESTINO,
                EstadoPedido.EN_REPARTO: TipoEventoTracking.EN_REPARTO,
                EstadoPedido.ENTREGADO: TipoEventoTracking.ENTREGADO,
                EstadoPedido.CANCELADO: TipoEventoTracking.CANCELADO,
                EstadoPedido.DEVUELTO: TipoEventoTracking.DEVUELTO_REMITENTE,
            }
            
            if nuevo_estado in evento_mapping:
                EventoTracking.objects.create(
                    pedido=self,
                    tipo_evento=evento_mapping[nuevo_estado],
                    ubicacion_texto=self.destino_completo,
                    registrado_por=usuario,
                    descripcion=f'Estado cambiado a {nuevo_estado}'
                )
        
        return True
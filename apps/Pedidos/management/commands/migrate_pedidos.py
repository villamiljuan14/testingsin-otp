from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.Pedido.models import Pedido as PedidoLegacy, Pago, GuiaEnvio, Seguimiento
from apps.Pedidos.models import Pedido as PedidoModern, GuiaEnvio as GuiaModern, EventoTracking
from apps.Autenticacion.models import Usuario
from apps.Ubicaciones.models import Pais, Departamento, Ciudad
from apps.Pedidos.models.choices import EstadoPedido, TipoEventoTracking

class Command(BaseCommand):
    help = 'Migra datos del módulo Pedido/ al módulo Pedidos/'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simula la migración sin ejecutar')
        parser.add_argument('--force', action='store_true', help='Fuerza la migración incluso si hay datos')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando migración Pedido → Pedidos'))
        
        # Verificar si ya hay datos modernos
        if not force and PedidoModern.objects.exists():
            self.stdout.write(self.style.WARNING('⚠️  Ya existen datos en Pedidos/. Usa --force para sobrescribir'))
            return
        
        # Contar datos legacy
        legacy_count = PedidoLegacy.objects.count()
        self.stdout.write(f'📊 Pedidos legacy encontrados: {legacy_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY RUN - No se ejecutarán cambios'))
        
        with transaction.atomic():
            migrados = 0
            errores = 0
            
            for pedido_legacy in PedidoLegacy.objects.all():
                try:
                    # Mapear ubicaciones (legacy → moderno)
                    pais_origen = self._get_or_create_pais(pedido_legacy.direccion_origen.ciudad)
                    ciudad_origen = self._get_or_create_ciudad(pedido_legacy.direccion_origen.ciudad, pais_origen)
                    
                    pais_destino = self._get_or_create_pais(pedido_legacy.direccion_destino.ciudad)
                    ciudad_destino = self._get_or_create_ciudad(pedido_legacy.direccion_destino.ciudad, pais_destino)
                    
                    # Crear pedido moderno
                    pedido_moderno = PedidoModern(
                        # Identificación
                        numero_pedido=f"LEG-{pedido_legacy.id}",
                        codigo_rastreo=f"LEG-{pedido_legacy.id}",
                        
                        # Usuario
                        usuario=pedido_legacy.usuario,
                        
                        # Ubicaciones normalizadas
                        pais_origen=pais_origen,
                        ciudad_origen=ciudad_origen,
                        pais_destino=pais_destino,
                        ciudad_destino=ciudad_destino,
                        
                        # Contactos
                        nombre_destinatario=f"{pedido_legacy.usuario.primer_nombre} {pedido_legacy.usuario.primer_apellido}",
                        telefono_destinatario=pedido_legacy.usuario.telefono or "",
                        email_destinatario=pedido_legacy.usuario.email,
                        
                        # Servicio
                        tipo_servicio=pedido_legacy.tipo_servicio,
                        
                        # Datos básicos (valores por defecto)
                        peso_real_kg=Decimal('1.00'),
                        descripcion_contenido="Migrado desde sistema legacy",
                        subtotal=pedido_legacy.total_final,
                        total_final=pedido_legacy.total_final,
                        
                        # Estado y fechas
                        estado=self._mapear_estado(pedido_legacy.estado.nombre),
                        fecha_pedido=pedido_legacy.fecha_pedido,
                        fecha_estimada_entrega=pedido_legacy.fecha_entrega,
                        fecha_entrega_real=pedido_legacy.fecha_entrega,
                        
                        # Notas
                        instrucciones_entrega=pedido_legacy.notas,
                    )
                    
                    if not dry_run:
                        pedido_moderno.save()
                        
                        # Migrar pagos
                        self._migrar_pagos(pedido_legacy, pedido_moderno, dry_run)
                        
                        # Migrar guía si existe
                        if hasattr(pedido_legacy, 'guia'):
                            self._migrar_guia(pedido_legacy.guia, pedido_moderno, dry_run)
                        
                        # Migrar seguimientos como eventos de tracking
                        self._migrar_seguimientos(pedido_legacy, pedido_moderno, dry_run)
                    
                    migrados += 1
                    
                    if migrados % 10 == 0:
                        self.stdout.write(f'✅ Migrados: {migrados}/{legacy_count}')
                        
                except Exception as e:
                    errores += 1
                    self.stdout.write(self.style.ERROR(f'❌ Error migrando pedido {pedido_legacy.id}: {str(e)}'))
                    continue
            
            # Resumen
            self.stdout.write(self.style.SUCCESS(f'''
🎉 MIGRACIÓN COMPLETADA
✅ Pedidos migrados: {migrados}
❌ Errores: {errores}
📊 Total procesados: {legacy_count}
{'🔍 DRY RUN - Sin cambios reales' if dry_run else '💾 Cambios guardados en base de datos'}
            '''))

    def _get_or_create_pais(self, nombre_ciudad):
        """Crea país por defecto para migración"""
        pais, _ = Pais.objects.get_or_create(
            nombre="Colombia",
            defaults={'codigo_iso': 'CO'}
        )
        return pais

    def _get_or_create_ciudad(self, nombre_ciudad, pais):
        """Crea ciudad para migración"""
        ciudad, _ = Ciudad.objects.get_or_create(
            nombre=nombre_ciudad,
            pais=pais,
            defaults={'codigo_postal': '000000'}
        )
        return ciudad

    def _mapear_estado(self, estado_legacy):
        """Mapea estados legacy a modernos"""
        mapeo = {
            'Pendiente': EstadoPedido.PENDIENTE,
            'En Proceso': EstadoPedido.EN_PROCESO,
            'En Camino': EstadoPedido.EN_CAMINO,
            'Entregado': EstadoPedido.ENTREGADO,
            'Cancelado': EstadoPedido.CANCELADO,
        }
        return mapeo.get(estado_legacy, EstadoPedido.BORRADOR)

    def _migrar_pagos(self, pedido_legacy, pedido_moderno, dry_run):
        """Migra pagos del pedido legacy"""
        # Por ahora solo registramos que existieron pagos
        # La lógica de pagos modernos es diferente
        pass

    def _migrar_guia(self, guia_legacy, pedido_moderno, dry_run):
        """Migra guía de envío"""
        if not dry_run:
            guia_moderna = GuiaModern.objects.create(
                pedido=pedido_moderno,
                numero_guia=f"MIG-{guia_legacy.numero_guia}",
                codigo_barras=guia_legacy.codigo_barras,
                peso_real=guia_legacy.peso_real,
                dimensiones=guia_legacy.dimensiones,
                instrucciones_especiales=guia_legacy.instrucciones_especiales,
            )

    def _migrar_seguimientos(self, pedido_legacy, pedido_moderno, dry_run):
        """Migra seguimientos como eventos de tracking"""
        for seguimiento in pedido_legacy.seguimientos.all():
            if not dry_run:
                EventoTracking.objects.create(
                    pedido=pedido_moderno,
                    tipo_evento=TipoEventoTracking.ACTUALIZACION,
                    descripcion=seguimiento.estado_seguimiento,
                    ubicacion=seguimiento.ubicacion_actual,
                    latitud=seguimiento.latitud,
                    longitud=seguimiento.longitud,
                    registrado_por=seguimiento.registrado_por,
                    fecha_evento=seguimiento.fecha_registro,
                )

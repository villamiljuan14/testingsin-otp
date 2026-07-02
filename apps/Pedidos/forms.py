from django import forms
from .models import Pedido, TipoServicio, Hub, GuiaEnvio, Reclamo


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nombre_destinatario',
            'telefono_destinatario', 
            'email_destinatario',
            'tipo_servicio',
            'estado',
            'pais_origen',
            'departamento_origen',
            'ciudad_origen',
            'direccion_origen_calle',
            'direccion_origen_numero',
            'direccion_origen_barrio',
            'direccion_origen_referencia',
            'pais_destino',
            'departamento_destino',
            'ciudad_destino',
            'direccion_destino_calle',
            'direccion_destino_numero',
            'direccion_destino_barrio',
            'direccion_destino_referencia',
            'hub_origen',
            'hub_destino',
            'peso_real_kg',
            'largo_cm',
            'ancho_cm',
            'alto_cm',
            'valor_declarado',
            'descripcion_contenido',
            'es_fragil',
            'requiere_firma',
        ]
        widgets = {
            'nombre_destinatario': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Nombre completo del destinatario'
            }),
            'telefono_destinatario': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '+57 300 000 0000'
            }),
            'email_destinatario': forms.EmailInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'correo@ejemplo.com'
            }),
            'tipo_servicio': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'pais_origen': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'departamento_origen': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'ciudad_origen': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'pais_destino': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'departamento_destino': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'ciudad_destino': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'hub_origen': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'hub_destino': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'peso_real_kg': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'largo_cm': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '0',
                'min': '0'
            }),
            'ancho_cm': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '0',
                'min': '0'
            }),
            'alto_cm': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '0',
                'min': '0'
            }),
            'valor_declarado': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'descripcion_contenido': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Describe el contenido del paquete...',
                'rows': 3
            }),
            'es_fragil': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 rounded'
            }),
            'requiere_firma': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 rounded'
            }),
            'direccion_origen_calle': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: Calle 123, Avenida Principal'
            }),
            'direccion_origen_numero': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: #45-67, Apto 302'
            }),
            'direccion_origen_barrio': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: El Poblado, Centro'
            }),
            'direccion_origen_referencia': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Casa de dos pisos, portón negro, cerca del supermercado...',
                'rows': 2
            }),
            'direccion_destino_calle': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: Carrera 45, Calle 67'
            }),
            'direccion_destino_numero': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: Torre A, Oficina 501'
            }),
            'direccion_destino_barrio': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: Zona Industrial, Norte'
            }),
            'direccion_destino_referencia': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Edificio azul, recepción en primer piso...',
                'rows': 2
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar datos para hubs (ya existentes)
        try:
            from apps.Ubicaciones.models import Pais, Departamento, Ciudad
            
            # Cargar hubs activos
            self.fields['hub_origen'].queryset = Hub.objects.filter(es_activo=True)
            self.fields['hub_destino'].queryset = Hub.objects.filter(es_activo=True)
            
            # Verificar si hay datos en las tablas de ubicaciones
            paises_count = Pais.objects.count()
            deptos_count = Departamento.objects.count()
            ciudades_count = Ciudad.objects.count()
            
            # Cargar países, departamentos y ciudades solo si existen datos
            if paises_count > 0:
                self.fields['pais_origen'].queryset = Pais.objects.all()
                self.fields['pais_destino'].queryset = Pais.objects.all()
            
            if deptos_count > 0:
                self.fields['departamento_origen'].queryset = Departamento.objects.all()
                self.fields['departamento_destino'].queryset = Departamento.objects.all()
            
            if ciudades_count > 0:
                self.fields['ciudad_origen'].queryset = Ciudad.objects.all()
                self.fields['ciudad_destino'].queryset = Ciudad.objects.all()
            
        except Exception as e:
            # Si hay error de importación o consulta, dejar los campos vacíos
            print(f"Error cargando datos de ubicación: {e}")
            pass
        
        # Configurar tipo_servicio
        try:
            from .models import TipoServicio
            self.fields['tipo_servicio'].queryset = TipoServicio.objects.all()
        except:
            pass
        
        # Personalizar labels
        self.fields['nombre_destinatario'].label = 'Nombre del Destinatario'
        self.fields['telefono_destinatario'].label = 'Teléfono de Contacto'
        self.fields['email_destinatario'].label = 'Email del Destinatario'
        self.fields['tipo_servicio'].label = 'Tipo de Servicio'
        self.fields['estado'].label = 'Estado del Pedido'
        self.fields['hub_origen'].label = 'Hub de Origen'
        self.fields['hub_destino'].label = 'Hub de Destino'
        self.fields['pais_origen'].label = 'País de Origen'
        self.fields['departamento_origen'].label = 'Departamento de Origen'
        self.fields['ciudad_origen'].label = 'Ciudad de Origen'
        self.fields['pais_destino'].label = 'País de Destino'
        self.fields['departamento_destino'].label = 'Departamento de Destino'
        self.fields['ciudad_destino'].label = 'Ciudad de Destino'
        self.fields['direccion_origen_calle'].label = 'Calle / Avenida (Origen)'
        self.fields['direccion_origen_numero'].label = 'Número / Apartamento'
        self.fields['direccion_origen_barrio'].label = 'Barrio / Colonia'
        self.fields['direccion_origen_referencia'].label = 'Referencias adicionales'
        self.fields['direccion_destino_calle'].label = 'Calle / Avenida (Destino)'
        self.fields['direccion_destino_numero'].label = 'Número / Apartamento'
        self.fields['direccion_destino_barrio'].label = 'Barrio / Colonia'
        self.fields['direccion_destino_referencia'].label = 'Referencias adicionales'
        self.fields['peso_real_kg'].label = 'Peso Real (kg)'
        self.fields['largo_cm'].label = 'Largo (cm)'
        self.fields['ancho_cm'].label = 'Ancho (cm)'
        self.fields['alto_cm'].label = 'Alto (cm)'
        self.fields['valor_declarado'].label = 'Valor Declarado ($)'
        self.fields['descripcion_contenido'].label = 'Descripción del Contenido'
        self.fields['es_fragil'].label = 'Es Frágil'
        self.fields['requiere_firma'].label = 'Requiere Firma'
        
        # Agregar placeholders y help texts
        self.fields['peso_real_kg'].help_text = 'Peso exacto del paquete en kilogramos'
        self.fields['largo_cm'].help_text = 'Largo del paquete en centímetros'
        self.fields['ancho_cm'].help_text = 'Ancho del paquete en centímetros'
        self.fields['alto_cm'].help_text = 'Alto del paquete en centímetros'
        self.fields['valor_declarado'].help_text = 'Valor declarado para fines de seguro'
        self.fields['descripcion_contenido'].help_text = 'Descripción detallada del contenido del paquete'
        self.fields['es_fragil'].help_text = 'Marcar si el contenido es frágil'
        self.fields['requiere_firma'].help_text = 'Requerir firma al momento de la entrega'
        self.fields['direccion_origen_calle'].help_text = 'Nombre de la calle o avenida donde se recogerá el paquete'
        self.fields['direccion_origen_numero'].help_text = 'Número de puerta, apartamento, piso, etc.'
        self.fields['direccion_origen_barrio'].help_text = 'Nombre del barrio, colonia o sector'
        self.fields['direccion_origen_referencia'].help_text = 'Indicaciones especiales para ubicar el lugar (color de casa, puntos de referencia, etc.)'
        self.fields['direccion_destino_calle'].help_text = 'Nombre de la calle o avenida donde se entregará el paquete'
        self.fields['direccion_destino_numero'].help_text = 'Número de puerta, apartamento, oficina, etc.'
        self.fields['direccion_destino_barrio'].help_text = 'Nombre del barrio, colonia o sector'
        self.fields['direccion_destino_referencia'].help_text = 'Indicaciones especiales para ubicar el lugar y entregar el paquete'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que origen y destino sean diferentes
        origen = cleaned_data.get('hub_origen')
        destino = cleaned_data.get('hub_destino')
        
        if origen and destino and origen == destino:
            raise forms.ValidationError('El hub de origen y destino no pueden ser iguales.')
        
        # Validar peso y valor
        peso = cleaned_data.get('peso_real_kg')
        valor = cleaned_data.get('valor_declarado')
        
        if peso and peso <= 0:
            raise forms.ValidationError('El peso debe ser mayor a 0.')
        
        if valor and valor <= 0:
            raise forms.ValidationError('El valor declarado debe ser mayor a 0.')
        
        return cleaned_data


class GuiaEnvioForm(forms.ModelForm):
    """Formulario para la gestión de guías de envío."""
    class Meta:
        model = GuiaEnvio
        fields = [
            'estado',
            'peso_final_kg',
            'dimensiones',
            'instrucciones_especiales',
            'es_fragil',
            'requiere_firma',
            'no_doblar',
        ]
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'peso_final_kg': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'step': '0.01',
                'min': '0.01'
            }),
            'dimensiones': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: 20x30x15 cm'
            }),
            'instrucciones_especiales': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'rows': 3,
                'placeholder': 'Indicaciones para el mensajero...'
            }),
            'es_fragil': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
            'requiere_firma': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
            'no_doblar': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels
        self.fields['estado'].label = 'Estado de la Guía'
        self.fields['peso_final_kg'].label = 'Peso Final (kg)'
        self.fields['dimensiones'].label = 'Dimensiones (LxAxAl)'
        self.fields['instrucciones_especiales'].label = 'Instrucciones Especiales'
        self.fields['es_fragil'].label = 'Contenido Frágil'
        self.fields['requiere_firma'].label = 'Requiere Firma al Entregar'
        self.fields['no_doblar'].label = 'No Doblar'


class HubForm(forms.ModelForm):
    """Formulario para la gestión de Hubs logísticos."""
    class Meta:
        model = Hub
        fields = [
            'nombre', 'codigo', 'tipo', 'es_activo',
            'direccion', 'ciudad', 'departamento', 'pais', 'codigo_postal',
            'latitud', 'longitud', 'telefono', 'email',
            'horario_inicio', 'horario_fin', 'hub_padre'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Nombre comercial del Hub'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ej: BOG-HUB-01'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
            'es_activo': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 rounded'}),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Dirección física completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Ciudad de operación'
            }),
            'departamento': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'placeholder': 'Departamento / Estado'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'step': '0.000001'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'step': '0.000001'
            }),
            'horario_inicio': forms.TimeInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'type': 'time'
            }),
            'horario_fin': forms.TimeInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 transition-all shadow-inner focus:outline-none',
                'type': 'time'
            }),
            'hub_padre': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 appearance-none shadow-inner focus:outline-none',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar etiquetas
        self.fields['es_activo'].label = '¿El Hub está operativo?'
        self.fields['hub_padre'].label = 'Hub Superior (Opcional)'
        self.fields['hub_padre'].help_text = 'Asigna un Hub Central si este es un Hub Regional o Local.'


class TipoServicioForm(forms.ModelForm):
    """Formulario para la gestión de tipos de servicio."""
    class Meta:
        model = TipoServicio
        fields = [
            'nombre', 'codigo', 'descripcion', 'es_activo',
            'dias_entrega_min', 'dias_entrega_max', 'es_garantizado',
            'costo_base', 'costo_por_kg', 'peso_max_kg',
            'largo_max_cm', 'ancho_max_cm', 'alto_max_cm',
            'es_nacional', 'es_internacional'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'codigo': forms.TextInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'rows': 3}),
            'costo_base': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'step': '0.01'}),
            'costo_por_kg': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'step': '0.01'}),
            'es_activo': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-emerald-600 rounded'}),
            'es_garantizado': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
            'es_nacional': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
            'es_internacional': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['dias_entrega_min', 'dias_entrega_max', 'peso_max_kg', 'largo_max_cm', 'ancho_max_cm', 'alto_max_cm']:
            self.fields[field].widget.attrs.update({'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'})


class ReclamoForm(forms.ModelForm):
    """Formulario para la radicación inicial de reclamos."""
    class Meta:
        model = Reclamo
        fields = [
            'pedido', 'tipo', 'prioridad', 'descripcion', 
            'nombre_reclamante', 'email_reclamante', 'telefono_reclamante',
            'valor_reclamado', 'descripcion_danos'
        ]
        widgets = {
            'pedido': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'tipo': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'prioridad': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'rows': 4}),
            'descripcion_danos': forms.Textarea(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'rows': 2}),
            'valor_reclamado': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['nombre_reclamante', 'email_reclamante', 'telefono_reclamante']:
            self.fields[field].widget.attrs.update({'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'})


class ReclamoResolucionForm(forms.ModelForm):
    """Formulario para la gestión administrativa de reclamos (Analistas)."""
    class Meta:
        model = Reclamo
        fields = [
            'estado', 'prioridad', 'asignado_a', 
            'valor_aprobado', 'resolucion', 'motivo_rechazo'
        ]
        widgets = {
            'estado': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'prioridad': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'asignado_a': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'}),
            'valor_aprobado': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'step': '0.01'}),
            'resolucion': forms.Textarea(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'rows': 4}),
            'motivo_rechazo': forms.Textarea(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none', 'rows': 2}),
        }



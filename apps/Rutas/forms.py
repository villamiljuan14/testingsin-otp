from django import forms
from django.utils import timezone
from django.db.models import Q
from .models import Vehiculo, Ruta, EstadoVehiculo, EstadoRuta, PrioridadRuta
from apps.core.mixins import StyleFormMixin

class VehiculoForm(forms.ModelForm):
    """Formulario avanzado para la gestión de flota vehicular (Modelo Modular)."""
    class Meta:
        model = Vehiculo
        fields = [
            'placa', 'marca', 'modelo', 'anio',
            'tipo_vehiculo', 'capacidad_volumen_m3', 'capacidad_peso_kg', 'estado'
        ]
        widgets = {
            'placa': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none uppercase',
                'placeholder': 'Ej: ABC-123'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'placeholder': 'Ej: Kenworth, Chevrolet'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'placeholder': 'Ej: T800, NPR'
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'min': '1990', 'max': '2030'
            }),
            'tipo_vehiculo': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'placeholder': 'Ej: VAN, TRUCK, MOTO'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none'
            }),
            'capacidad_volumen_m3': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary shadow-inner outline-none', 'step': '0.1'}),
            'capacidad_peso_kg': forms.NumberInput(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary shadow-inner outline-none', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capacidad_volumen_m3'].label = 'Volumen (m³)'
        self.fields['capacidad_peso_kg'].label = 'Carga Máx (kg)'


class RutaForm(forms.ModelForm):
    """Formulario para la programación y despacho de rutas (Modelo Modular)."""
    class Meta:
        model = Ruta
        fields = ['nombre', 'hub_origen', 'hub_destino', 'vehiculo', 'conductor', 'estado', 'prioridad', 'fecha_programada', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'placeholder': 'Ej: RUTA-NORTE-BOG-01'
            }),
            'hub_origen': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'hub_destino': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'vehiculo': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'conductor': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'estado': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'prioridad': forms.Select(attrs={'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary appearance-none shadow-inner outline-none'}),
            'fecha_programada': forms.DateInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm text-custom-primary placeholder:text-custom-outline focus:ring-2 focus:ring-blue-500/20 shadow-inner outline-none',
                'rows': 3,
                'placeholder': 'Detalles adicionales de la ruta...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.Autenticacion.models import Usuario, TipoRol
        # ✅ Filtro estricto: Solo usuarios con rol de MENSAJERO
        self.fields['conductor'].queryset = Usuario.objects.filter(
            rol__tipo_rol=TipoRol.MENSAJERO,
            is_active=True
        )
        # ✅ Filtro: Solo vehículos disponibles o el ya asignado a esta ruta
        from .models import EstadoVehiculo
        if self.instance.pk and self.instance.vehiculo:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
                Q(estado=EstadoVehiculo.DISPONIBLE) | Q(pk=self.instance.vehiculo.pk)
            )
        else:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(estado=EstadoVehiculo.DISPONIBLE)

    def clean_fecha_programada(self):
        fecha = self.cleaned_data.get('fecha_programada')
        hoy = timezone.now().date()
        if fecha and fecha < hoy:
            raise forms.ValidationError("La fecha programada no puede ser anterior a la fecha actual.")
        return fecha
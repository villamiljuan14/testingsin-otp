from django import forms
from .models.tracking import EventoTracking


class EventoTrackingForm(forms.ModelForm):
    """Formulario para crear/editar eventos de tracking"""
    
    class Meta:
        model = EventoTracking
        fields = [
            'pedido', 'guia', 'tipo_evento', 'hub',
            'ubicacion_texto', 'latitud', 'longitud',
            'descripcion', 'observaciones', 'evidencia_foto', 'evidencia_documento'
        ]
        widgets = {
            'pedido': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
            'guia': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
            'tipo_evento': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
            'hub': forms.Select(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
            'ubicacion_texto': forms.TextInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm',
                'placeholder': 'Ej: Hub Bogotá, Calle 123'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm',
                'placeholder': '4.7110'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm',
                'placeholder': '-74.0721'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm',
                'rows': 3,
                'placeholder': 'Descripción del evento...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm',
                'rows': 2,
                'placeholder': 'Observaciones adicionales...'
            }),
            'evidencia_foto': forms.FileInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
            'evidencia_documento': forms.FileInput(attrs={
                'class': 'w-full bg-custom-surface border border-custom-ui rounded-xl py-3 px-4 text-sm'
            }),
        }

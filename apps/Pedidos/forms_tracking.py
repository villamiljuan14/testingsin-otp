from django import forms
from .models.tracking import EventoTracking
from .models.choices import TipoEventoTracking


class EventoTrackingForm(forms.ModelForm):
    """Formulario para crear/editar eventos de tracking.
    Si el evento ya existe y su tipo es ENTREGADO, el campo tipo_evento
    queda como solo lectura para reforzar la inmutabilidad en la UI.
    """

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un evento ENTREGADO, bloquear tipo_evento
        if self.instance and self.instance.pk:
            if self.instance.tipo_evento == TipoEventoTracking.ENTREGADO:
                self.fields['tipo_evento'].disabled = True
                self.fields['tipo_evento'].help_text = (
                    'Este evento corresponde a una entrega confirmada y no puede modificarse.'
                )

    def clean(self):
        """Impide crear nuevos eventos si el pedido ya tiene un evento ENTREGADO."""
        cleaned_data = super().clean()
        pedido = cleaned_data.get('pedido')

        # Solo aplica en creación (sin pk aún)
        if pedido and not self.instance.pk:
            ya_entregado = EventoTracking.objects.filter(
                pedido=pedido,
                tipo_evento=TipoEventoTracking.ENTREGADO
            ).exists()
            if ya_entregado:
                raise forms.ValidationError(
                    f'El pedido #{pedido.numero_pedido} ya fue marcado como Entregado. '
                    f'No se pueden registrar más eventos de tracking para este pedido.'
                )
        return cleaned_data
        """Impide cambiar tipo_evento si el evento original fue ENTREGADO."""
        tipo = self.cleaned_data.get('tipo_evento')
        if self.instance and self.instance.pk:
            original = EventoTracking.objects.filter(
                pk=self.instance.pk
            ).values('tipo_evento').first()
            if original and original['tipo_evento'] == TipoEventoTracking.ENTREGADO:
                # Devuelve el valor original, ignorando cualquier cambio
                return original['tipo_evento']
        return tipo

from django import forms
from .models import NovedadPedido
from apps.core.mixins import StyleFormMixin

class NovedadPedidoForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = NovedadPedido
        fields = ['pedido', 'usuario', 'titulo', 'tipo_novedad', 'descripcion', 'fecha_novedad']
        widgets = {
            'fecha_novedad': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

from django import forms

class StyleFormMixin:
    """Mixin para aplicar estilos consistentes a los formularios de Enviart."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500/50 focus:ring-offset-slate-900 transition-all'
                })
            elif isinstance(field.widget, (forms.Select, forms.TextInput, forms.EmailInput, forms.PasswordInput, forms.NumberInput, forms.DateTimeInput)):
                field.widget.attrs.update({
                    'class': 'w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all text-slate-200 placeholder-slate-500'
                })

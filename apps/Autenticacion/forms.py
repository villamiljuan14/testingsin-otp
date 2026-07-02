from django import forms
from django.core.exceptions import ValidationError
from apps.core.mixins import StyleFormMixin

# 🟢 IMPORTACIONES ABSOLUTAS (Corregidas para evitar el ModuleNotFoundError)
from apps.Autenticacion.models.usuario import Usuario
from apps.Autenticacion.services.validation_service import UsuarioValidationService
from apps.Autenticacion.validators import validar_documento

class UsuarioForm(StyleFormMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False, attrs={'placeholder': '********'}),
        required=True,
        help_text="Establece una contraseña segura."
    )

    class Meta:
        model = Usuario
        fields = [
            'email', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'tipo_documento', 'doc_usuario', 'telefono', 'rol', 'is_active', 'is_staff'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+57 300 000 0000'}),
            'doc_usuario': forms.TextInput(attrs={'placeholder': 'Número de documento'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['password'].help_text = "Deja en blanco para mantener la contraseña actual."
    
    def clean_email(self):
        """Validate email is unique using validation service."""
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('El email no puede estar vacío.')
        
        email = UsuarioValidationService.normalize_email(email)
        exclude_id = self.instance.pk if self.instance.pk else None
        is_unique, error_msg = UsuarioValidationService.validate_email_unique(email, exclude_id)
        
        if not is_unique:
            raise forms.ValidationError(error_msg)
        return email
    
    def clean_doc_usuario(self):
        """Valida unicidad del documento en la base de datos."""
        doc_usuario = self.cleaned_data.get('doc_usuario', '').strip()
        if not doc_usuario:
            raise forms.ValidationError('El documento no puede estar vacío.')
        
        doc_usuario = doc_usuario.upper().strip()
        exclude_id = self.instance.pk if self.instance.pk else None
        
        is_unique, error_msg = UsuarioValidationService.validate_document_unique(doc_usuario, exclude_id=exclude_id)
        if not is_unique:
            raise forms.ValidationError(error_msg)
        
        return doc_usuario
    
    def clean_telefono(self):
        """Validate phone number format using validation service."""
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:  # El teléfono es opcional
            is_valid, error_msg = UsuarioValidationService.validate_phone(telefono)
            if not is_valid:
                raise forms.ValidationError(error_msg)
        return telefono
    
    def clean_password(self):
        """Validate password strength using validation service."""
        password = self.cleaned_data.get('password', '')
        
        if not password and not self.instance.pk:
            raise forms.ValidationError('La contraseña es obligatoria al crear un nuevo usuario.')
        
        if password:
            is_valid, errors = UsuarioValidationService.validate_password(password)
            if not is_valid:
                error_msg = ' '.join(errors)
                raise forms.ValidationError(error_msg)
        return password
    
    def clean(self):
        """Validación cruzada avanzada (Nombres, Rol y Tipo/Número de documento)."""
        cleaned_data = super().clean()
        
        primer_nombre = cleaned_data.get('primer_nombre', '').strip()
        primer_apellido = cleaned_data.get('primer_apellido', '').strip()
        
        if not primer_nombre:
            self.add_error('primer_nombre', 'El primer nombre es obligatorio.')
        
        if not primer_apellido:
            self.add_error('primer_apellido', 'El primer apellido es obligatorio.')
        
        rol = cleaned_data.get('rol')
        if not rol:
            self.add_error('rol', 'Debes seleccionar un rol.')
            
        # ──────────────────────────────────────────────────────────
        # VALIDACIÓN CRUCIAL: Validación de longitud según Tipo de Documento
        # ──────────────────────────────────────────────────────────
        tipo_documento = cleaned_data.get('tipo_documento')
        doc_usuario = cleaned_data.get('doc_usuario')
        
        if tipo_documento and doc_usuario:
            try:
                # Reutilizamos tu validador estricto global
                validar_documento(doc_usuario, tipo_documento)
            except ValidationError as e:
                # 🛠️ Solución robusta para extraer el string del error de Django de forma segura
                self.add_error('doc_usuario', e.messages[0])
        
        return cleaned_data
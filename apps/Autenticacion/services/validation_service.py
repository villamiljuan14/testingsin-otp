"""
Usuario Validation Service - Handles all validation rules for usuarios.

This service provides:
- Password strength validation
- Unique constraint checking (email, document)
- Data normalization and sanitization
- Custom business rule validation
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db.models import Q

from .base import ServiceBase
from ..models import Usuario, TipoDocumento

logger = logging.getLogger(__name__)


class UsuarioValidationService(ServiceBase):
    """
    Service for validating usuario data and enforcing business rules.
    """
    
    # Password validation constants
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength according to security requirements.
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        
        Args:
            password: Password string to validate
        
        Returns:
            Tuple of (is_valid, errors_list)
            - is_valid: True if password passes all checks
            - errors_list: List of validation error messages
        """
        errors = []
        
        if not password:
            errors.append('Password cannot be empty.')
            return False, errors
        
        # Check minimum length
        if len(password) < UsuarioValidationService.PASSWORD_MIN_LENGTH:
            errors.append(
                f'Password must be at least {UsuarioValidationService.PASSWORD_MIN_LENGTH} '
                'characters long.'
            )
        
        # Check for uppercase
        if UsuarioValidationService.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        
        # Check for lowercase
        if UsuarioValidationService.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        
        # Check for digit
        if UsuarioValidationService.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append('Password must contain at least one digit.')
        
        # Check for special characters (optional but recommend)
        if UsuarioValidationService.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character.')
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_email_unique(email: str, exclude_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Check if email is unique in the database.
        
        Args:
            email: Email address to check
            exclude_id: Usuario ID to exclude from check (for update operations)
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        if not email or not email.strip():
            return False, 'Email cannot be empty.'
        
        query = Usuario.objects.filter(email=email.strip())
        
        # Exclude current usuario when updating
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        if query.exists():
            return False, 'This email is already registered.'
        
        return True, ''
    
    @staticmethod
    def validate_document_unique(
        doc_usuario: str,
        tipo_documento: str = None,
        exclude_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Check if document number is unique in the database.
        
        Args:
            doc_usuario: Document number to check
            tipo_documento: Type of document (optional, for reference)
            exclude_id: Usuario ID to exclude from check (for update operations)
        
        Returns:
            Tuple of (is_unique, error_message)
        """
        if not doc_usuario or not doc_usuario.strip():
            return False, 'Document number cannot be empty.'
        
        query = Usuario.objects.filter(doc_usuario=doc_usuario.strip())
        
        # Exclude current usuario when updating
        if exclude_id:
            query = query.exclude(id=exclude_id)
        
        if query.exists():
            return False, f'Document number {doc_usuario} is already registered.'
        
        return True, ''
    
    @staticmethod
    def validate_document_format(
        doc_usuario: str,
        tipo_documento: str = None
    ) -> Tuple[bool, str]:
        """
        Validate document format based on type.
        
        Args:
            doc_usuario: Document number to validate
            tipo_documento: Type of document (CC, TI, CE, PP, etc.)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not doc_usuario or not doc_usuario.strip():
            return False, 'Document number cannot be empty.'
        
        # Remove spaces and special chars for validation
        cleaned = doc_usuario.strip().replace('-', '').replace(' ', '')
        
        # Basic validation: should be alphanumeric
        if not cleaned.isalnum():
            return False, 'Document must contain only letters and numbers.'
        
        # Check minimum length (typically documents are 5+ chars)
        if len(cleaned) < 5:
            return False, 'Document number is too short.'
        
        return True, ''
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone or not phone.strip():
            return True, ''  # Phone is optional
        
        # Remove common formatting chars
        cleaned = phone.strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Should be mostly numeric
        if not re.search(r'\d', cleaned):
            return False, 'Phone must contain at least one digit.'
        
        # Reasonable length: 7-15 digits
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) < 7 or len(digits) > 15:
            return False, 'Phone number should contain between 7 and 15 digits.'
        
        return True, ''
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize name: strip, capitalize, remove extra spaces.
        
        Args:
            name: Name to normalize
        
        Returns:
            Normalized name string
        """
        if not name:
            return ''
        
        # Strip and collapse multiple spaces
        normalized = ' '.join(name.strip().split())
        
        # Capitalize first letter of each word
        normalized = normalized.title()
        
        return normalized
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email: strip, lowercase.
        
        Args:
            email: Email to normalize
        
        Returns:
            Normalized email string
        """
        if not email:
            return ''
        
        return email.strip().lower()
    
    @staticmethod
    def prepare_user_data(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict]:
        """
        Prepare and normalize user data for storage.
        
        This method:
        1. Normalizes name fields
        2. Normalizes email
        3. Strips whitespace from strings
        4. Validates critical fields
        5. Returns cleaned data and any errors found
        
        Args:
            data: Raw user data dictionary
        
        Returns:
            Tuple of (cleaned_data, errors)
        """
        cleaned = {}
        errors = {}
        
        # Process name fields
        name_fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido']
        for field in name_fields:
            if field in data and data[field]:
                cleaned[field] = UsuarioValidationService.normalize_name(data[field])
            elif field in data:
                cleaned[field] = data[field]  # Keep as is (empty/None)
        
        # Process email
        if 'email' in data and data['email']:
            cleaned['email'] = UsuarioValidationService.normalize_email(data['email'])
            is_unique, error_msg = UsuarioValidationService.validate_email_unique(
                cleaned['email'],
                exclude_id=data.get('exclude_id')
            )
            if not is_unique:
                errors['email'] = error_msg
        
        # Process document
        if 'doc_usuario' in data and data['doc_usuario']:
            cleaned['doc_usuario'] = data['doc_usuario'].strip().upper()
            is_valid, error_msg = UsuarioValidationService.validate_document_format(
                cleaned['doc_usuario']
            )
            if not is_valid:
                errors['doc_usuario'] = error_msg
            
            is_unique, error_msg = UsuarioValidationService.validate_document_unique(
                cleaned['doc_usuario'],
                exclude_id=data.get('exclude_id')
            )
            if not is_unique:
                errors['doc_usuario'] = error_msg
        
        # Process phone
        if 'telefono' in data and data['telefono']:
            is_valid, error_msg = UsuarioValidationService.validate_phone(data['telefono'])
            if not is_valid:
                errors['telefono'] = error_msg
            else:
                cleaned['telefono'] = data['telefono'].strip()
        
        # Copy other fields as-is
        for key, value in data.items():
            if key not in cleaned and key != 'exclude_id':
                cleaned[key] = value
        
        return cleaned, errors
    
    @staticmethod
    def validate_rol_exists(rol_id: int) -> Tuple[bool, str]:
        """
        Verify that a rol exists.
        
        Args:
            rol_id: ID of the Rol to check
        
        Returns:
            Tuple of (exists, error_message)
        """
        from ..models import Rol
        
        if not UsuarioValidationService.is_valid_id(rol_id):
            return False, 'Invalid rol ID.'
        
        if not Rol.objects.filter(id=rol_id).exists():
            return False, f'Rol with ID {rol_id} does not exist.'
        
        return True, ''

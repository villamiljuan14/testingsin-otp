"""
WOMPI Payment Gateway Service Module
Handles payment processing, signature generation, and webhook validation
Supports both Sandbox and Production environments
"""

import hashlib
from django.conf import settings
from django.contrib import messages
from typing import Dict, Any, Optional, Tuple


class WompiService:
    """Service class for WOMPI payment gateway integration"""
    
    def __init__(self):
        """Initialize WOMPI service with environment-specific settings"""
        self.mode = settings.WOMPI_MODE
        self.public_key = settings.WOMPI_PUBLIC_KEY
        self.private_key = settings.WOMPI_PRIVATE_KEY
        self.integrity_secret = settings.WOMPI_INTEGRITY_SECRET
        self.events_secret = settings.WOMPI_EVENTS_SECRET
        self.api_url = settings.WOMPI_API_URL
        self.widget_url = settings.WOMPI_WIDGET_URL
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get current WOMPI environment configuration"""
        return {
            'mode': self.mode,
            'is_sandbox': self.mode == 'sandbox',
            'is_production': self.mode == 'production',
            'api_url': self.api_url,
            'widget_url': self.widget_url,
            'public_key_preview': self.public_key[:20] + '...' if self.public_key else 'Not configured',
        }
    
    def generate_integrity_signature(
        self,
        referencia: str,
        monto_en_centavos: int,
        moneda: str = 'COP'
    ) -> str:
        """
        Generate SHA256 integrity signature for WOMPI payment
        
        Formula: reference + amount_in_cents + currency + integrity_secret
        
        Args:
            referencia: Payment reference (e.g., 'PED-2026-000001-TX1')
            monto_en_centavos: Amount in cents (e.g., 5,000,000 for $50,000 COP)
            moneda: Currency code (default: 'COP')
        
        Returns:
            SHA256 hex digest
        
        Raises:
            ValueError: If integrity secret is not configured
        """
        if not self.integrity_secret:
            raise ValueError(
                f"WOMPI integrity secret not configured for {self.mode} mode. "
                f"Set WOMPI_{'PRODUCTION' if self.mode == 'production' else 'SANDBOX'}_INTEGRITY_SECRET"
            )
        
        cadena = f"{referencia}{monto_en_centavos}{moneda}{self.integrity_secret}"
        return hashlib.sha256(cadena.encode('utf-8')).hexdigest()
    
    def generate_event_checksum(
        self,
        properties_values: str,
        timestamp: str
    ) -> str:
        """
        Generate checksum for webhook event validation
        
        Args:
            properties_values: Concatenated values of transaction properties
            timestamp: Event timestamp
        
        Returns:
            SHA256 hex digest
        
        Raises:
            ValueError: If events secret is not configured
        """
        if not self.events_secret:
            raise ValueError(
                f"WOMPI events secret not configured for {self.mode} mode. "
                f"Set WOMPI_{'PRODUCTION' if self.mode == 'production' else 'SANDBOX'}_EVENTS_SECRET"
            )
        
        cadena = f"{properties_values}{timestamp}{self.events_secret}"
        return hashlib.sha256(cadena.encode('utf-8')).hexdigest()
    
    def validate_webhook_signature(
        self,
        checksum_recibido: str,
        properties_values: str,
        timestamp: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate webhook signature to ensure event authenticity
        
        Args:
            checksum_recibido: Checksum received from WOMPI
            properties_values: Concatenated values of transaction properties
            timestamp: Event timestamp
        
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            checksum_calculado = self.generate_event_checksum(properties_values, timestamp)
            
            if checksum_recibido != checksum_calculado:
                return False, "Webhook signature validation failed"
            
            return True, None
        except Exception as e:
            return False, f"Webhook validation error: {str(e)}"
    
    def prepare_checkout_context(
        self,
        pedido,
        request_build_absolute_uri_func
    ) -> Dict[str, Any]:
        """
        Prepare context data for checkout template
        
        Args:
            pedido: Pedido model instance
            request_build_absolute_uri_func: request.build_absolute_uri function
        
        Returns:
            Dictionary with all checkout context data
        """
        # Convert amount to cents (Wompi requires amounts in cents)
        monto_en_centavos = int(pedido.total_final * 100)
        moneda = "COP"
        
        import time
        # Generate unique payment reference appending a timestamp to avoid duplicate reference errors
        referencia = f"{pedido.numero_pedido}-TX{pedido.id}-{int(time.time())}"
        
        # Generate integrity signature
        firma = self.generate_integrity_signature(referencia, monto_en_centavos, moneda)
        
        return {
            'pedido': pedido,
            'wompi_public_key': self.public_key,
            'wompi_widget_url': self.widget_url,
            'wompi_mode': self.mode,
            'monto_en_centavos': monto_en_centavos,
            'referencia': referencia,
            'moneda': moneda,
            'firma': firma,
            'redirect_url': request_build_absolute_uri_func('/dashboard/pedidos/'),
            'is_sandbox': self.mode == 'sandbox',
        }
    
    def log_checkout_attempt(self, referencia: str, monto_en_centavos: int, firma: str) -> None:
        """Log checkout attempt for debugging"""
        env_info = "🧪 SANDBOX MODE" if self.mode == 'sandbox' else "🏭 PRODUCTION MODE"
        print(f"\n{'='*60}")
        print(f"🔐 WOMPI CHECKOUT ATTEMPT - {env_info}")
        print(f"{'='*60}")
        print(f"🔑 Public Key: {self.public_key[:20]}...")
        print(f"📝 Reference: {referencia}")
        print(f"💰 Amount (cents): {monto_en_centavos}")
        print(f"✍️  SHA256 Signature: {firma}")
        print(f"{'='*60}\n")
    
    def get_payment_method_display(self, method_code: str) -> str:
        """Convert WOMPI payment method code to display name"""
        payment_methods = {
            'CARD': 'Tarjeta de Crédito/Débito',
            'TRANSFER': 'Transferencia Bancaria',
            'NEQUI': 'Nequi',
            'DAVIPLATA': 'Daviplata',
            'BANKACCOUNT': 'Cuenta Bancaria',
        }
        return payment_methods.get(method_code, method_code)
    
    def map_wompi_status_to_pedido_status(self, wompi_status: str) -> Optional[str]:
        """
        Map WOMPI transaction status to Pedido status
        
        Args:
            wompi_status: WOMPI status code (APPROVED, DECLINED, ERROR, PENDING)
        
        Returns:
            Pedido status code or None if not mappable
        """
        from apps.Pedidos.models.choices import EstadoPedido
        
        status_map = {
            'APPROVED': EstadoPedido.CONFIRMADO,
            'DECLINED': EstadoPedido.PAGO_FALLIDO,
            'ERROR': EstadoPedido.PAGO_FALLIDO,
            'PENDING': EstadoPedido.PENDIENTE_PAGO,
        }
        return status_map.get(wompi_status)


# Singleton instance for easy import and use
_wompi_service_instance = None


def get_wompi_service() -> WompiService:
    """Get or create singleton WompiService instance"""
    global _wompi_service_instance
    if _wompi_service_instance is None:
        _wompi_service_instance = WompiService()
    return _wompi_service_instance

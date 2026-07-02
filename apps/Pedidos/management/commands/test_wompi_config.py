"""
Management command to test WOMPI payment gateway configuration
Usage: python manage.py test_wompi_config
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.Pedidos.services.wompi_service import get_wompi_service


class Command(BaseCommand):
    help = 'Test WOMPI payment gateway configuration and generate test signatures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate-signature',
            type=str,
            help='Generate test signature for given reference (e.g., PED-2026-000001-TX1)'
        )
        parser.add_argument(
            '--amount',
            type=int,
            default=1205000,
            help='Amount in cents for signature generation (default: 1205000 = $12,050 COP)'
        )
        parser.add_argument(
            '--mode',
            choices=['sandbox', 'production'],
            help='Override WOMPI_MODE for testing'
        )

    def handle(self, *args, **options):
        wompi_service = get_wompi_service()
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('🔐 WOMPI PAYMENT GATEWAY CONFIGURATION TEST')
        self.stdout.write('='*70 + '\n')
        
        # Show environment info
        env_info = wompi_service.get_environment_info()
        
        self.stdout.write(self.style.SUCCESS('Environment Status:'))
        self.stdout.write(f"  Mode: {self.style.WARNING(env_info['mode'].upper())}")
        self.stdout.write(f"  Sandbox: {self.style.HTTP_INFO(str(env_info['is_sandbox']))}")
        self.stdout.write(f"  Production: {self.style.HTTP_NOT_MODIFIED(str(env_info['is_production']))}")
        self.stdout.write(f"  API URL: {env_info['api_url']}")
        self.stdout.write(f"  Widget URL: {env_info['widget_url']}\n")
        
        # Check credentials
        self.stdout.write(self.style.SUCCESS('Credentials Status:'))
        
        if wompi_service.public_key:
            self.stdout.write(f"  ✅ Public Key: {wompi_service.public_key[:30]}...")
        else:
            self.stdout.write(self.style.ERROR("  ❌ Public Key: NOT CONFIGURED"))
        
        if wompi_service.private_key:
            self.stdout.write(f"  ✅ Private Key: {wompi_service.private_key[:30]}...")
        else:
            self.stdout.write(self.style.WARNING("  ⚠️  Private Key: NOT CONFIGURED (optional)"))
        
        if wompi_service.integrity_secret:
            self.stdout.write(f"  ✅ Integrity Secret: {wompi_service.integrity_secret[:30]}...")
        else:
            self.stdout.write(self.style.ERROR("  ❌ Integrity Secret: NOT CONFIGURED"))
        
        if wompi_service.events_secret:
            self.stdout.write(f"  ✅ Events Secret: {wompi_service.events_secret[:30]}...")
        else:
            self.stdout.write(self.style.WARNING("  ⚠️  Events Secret: NOT CONFIGURED (optional)"))
        
        self.stdout.write('')
        
        # Generate test signature if requested
        if options['generate_signature']:
            referencia = options['generate_signature']
            monto = options['amount']
            
            self.stdout.write(self.style.SUCCESS('Test Signature Generation:'))
            self.stdout.write(f"  Reference: {referencia}")
            self.stdout.write(f"  Amount (cents): {monto}")
            self.stdout.write(f"  Amount (pesos): ${monto/100:,.2f} COP")
            
            try:
                firma = wompi_service.generate_integrity_signature(
                    referencia,
                    monto,
                    'COP'
                )
                self.stdout.write(f"  SHA256 Signature: {self.style.SUCCESS(firma)}\n")
                
                # Display complete checkout parameters
                self.stdout.write(self.style.SUCCESS('Checkout Parameters:'))
                self.stdout.write(f"""
  data-public-key="{wompi_service.public_key}"
  data-reference="{referencia}"
  data-amount-in-cents="{monto}"
  data-currency="COP"
  data-integrity-signature="{firma}"
  data-redirect-url="https://your-domain.com/dashboard/pedidos/"
                """)
                
            except Exception as e:
                raise CommandError(f"Error generating signature: {str(e)}")
        
        # Configuration validation
        self.stdout.write(self.style.SUCCESS('\nConfiguration Validation:'))
        
        if not wompi_service.public_key:
            self.stdout.write(self.style.ERROR(
                "  ❌ CRITICAL: Public Key is required. Set WOMPI_SANDBOX_PUBLIC_KEY or WOMPI_PRODUCTION_PUBLIC_KEY"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Public Key is configured"))
        
        if not wompi_service.integrity_secret:
            self.stdout.write(self.style.ERROR(
                "  ❌ CRITICAL: Integrity Secret is required. Set WOMPI_SANDBOX_INTEGRITY_SECRET or WOMPI_PRODUCTION_INTEGRITY_SECRET"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Integrity Secret is configured"))
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('💡 Next Steps:')
        self.stdout.write('='*70)
        
        if env_info['is_sandbox']:
            self.stdout.write("""
1. Use the test credentials provided by WOMPI
2. Test the payment flow with Sandbox cards:
   - Visa: 4242 4242 4242 4242 (any future expiry, any CVC)
   - Mastercard: 5555 5555 5555 4444
3. Test webhooks using WOMPI's webhook simulation tool
4. Monitor logs for payment events
5. When ready, switch to PRODUCTION mode by setting WOMPI_MODE=production
            """)
        else:
            self.stdout.write("""
1. Ensure all production credentials are correctly set
2. Test payment flow with real cards on production account
3. Monitor transaction activity in WOMPI dashboard
4. Verify webhook endpoints are receiving events
5. Monitor payment status updates in your system
            """)
        
        self.stdout.write('='*70 + '\n')

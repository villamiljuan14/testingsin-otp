"""
Email backend personalizado para Resend API
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
import resend


class ResendEmailBackend(BaseEmailBackend):
    """
    Backend de email que usa la API de Resend
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.environ.get('RESEND_API_KEY', '')
        if self.api_key:
            resend.api_key = self.api_key

    def send_messages(self, email_messages):
        """
        Envía una lista de EmailMessage usando la API de Resend
        """
        if not self.api_key:
            # Si no hay API key, imprimir en consola para desarrollo
            for message in email_messages:
                self._print_to_console(message)
            return len(email_messages)

        sent_count = 0
        for message in email_messages:
            try:
                self._send_resend(message)
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                # Imprimir error en consola
                print(f"Error enviando email con Resend: {e}")
                self._print_to_console(message)
        return sent_count

    def _send_resend(self, message):
        """
        Envía un email individual usando la API de Resend
        """
        params = {
            "from": message.from_email,
            "to": message.to,
            "subject": message.subject,
            "html": message.body,
        }

        # Agregar CC si existe
        if message.cc:
            params["cc"] = message.cc

        # Agregar BCC si existe
        if message.bcc:
            params["bcc"] = message.bcc

        # Agregar reply_to si existe
        if message.reply_to:
            params["reply_to"] = message.reply_to[0] if isinstance(message.reply_to, list) else message.reply_to

        # Enviar usando la API de Resend
        resend.Emails.send(params)

    def _print_to_console(self, message):
        """
        Imprime el email en consola para desarrollo
        """
        print(f"\n{'='*50}")
        print(f"EMAIL (Console Backend - Resend no configurado)")
        print(f"{'='*50}")
        print(f"From: {message.from_email}")
        print(f"To: {message.to}")
        print(f"Subject: {message.subject}")
        print(f"{'-'*50}")
        print(f"Body:\n{message.body}")
        print(f"{'='*50}\n")

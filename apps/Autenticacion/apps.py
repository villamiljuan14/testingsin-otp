from django.apps import AppConfig


class AutenticacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Define la ruta absoluta para que Django encuentre la app en la nueva estructura
    name = 'apps.Autenticacion'
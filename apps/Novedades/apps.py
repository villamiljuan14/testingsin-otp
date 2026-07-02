from django.apps import AppConfig


class NovedadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Novedades'
    label = 'Novedades'
    verbose_name = 'Novedades e Incidencias'
    
    def ready(self):
        # import apps.Novedades.signals
        pass
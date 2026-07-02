from django.apps import AppConfig


class PedidosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Pedidos'
    label = 'Pedidos'
    verbose_name = 'Pedidos y Envíos'
    
    def ready(self):
        import apps.Pedidos.signals
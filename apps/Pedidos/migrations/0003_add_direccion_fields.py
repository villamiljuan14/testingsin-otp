# Generated manually - Add address fields to Pedido model

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('Pedidos', '0002_alter_pedido_ruta_alter_pedido_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='direccion_origen_calle',
            field=models.CharField(blank=True, max_length=200, null=True, help_text='Calle/Avenida de origen'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_origen_numero',
            field=models.CharField(blank=True, max_length=20, null=True, help_text='Número de puerta/edificio'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_origen_barrio',
            field=models.CharField(blank=True, max_length=100, null=True, help_text='Barrio/Colonia'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_origen_referencia',
            field=models.TextField(blank=True, null=True, help_text='Referencias adicionales para encontrar el lugar'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_destino_calle',
            field=models.CharField(blank=True, max_length=200, null=True, help_text='Calle/Avenida de destino'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_destino_numero',
            field=models.CharField(blank=True, max_length=20, null=True, help_text='Número de puerta/edificio'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_destino_barrio',
            field=models.CharField(blank=True, max_length=100, null=True, help_text='Barrio/Colonia'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='direccion_destino_referencia',
            field=models.TextField(blank=True, null=True, help_text='Referencias adicionales para encontrar el lugar'),
        ),
    ]

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidos', '0006_alter_pedido_estado_pago'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialUbicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitud', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitud', models.DecimalField(decimal_places=6, max_digits=9)),
                ('precision_gps', models.FloatField(blank=True, null=True)),
                ('registrado_en', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_ubicaciones', to='Pedidos.pedido')),
            ],
            options={
                'verbose_name': 'Historial de ubicación',
                'verbose_name_plural': 'Historial de ubicaciones',
                'db_table': 'pedidos_historial_ubicacion',
                'ordering': ['registrado_en'],
                'indexes': [models.Index(fields=['pedido', 'registrado_en'], name='pedidos_his_pedido__a1b2c3_idx')],
            },
        ),
    ]

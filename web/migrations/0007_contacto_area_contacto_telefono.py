# Generated by Django 4.2 on 2024-10-24 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_alojamiento_carrito_contacto_contadorsolicitudes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contacto',
            name='area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='web.areaservicio'),
        ),
        migrations.AddField(
            model_name='contacto',
            name='telefono',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]

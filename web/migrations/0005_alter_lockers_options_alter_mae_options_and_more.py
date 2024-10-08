# Generated by Django 4.2 on 2024-09-17 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_edificio_alter_solicitud_options_areaservicio_imagen_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lockers',
            options={'verbose_name': 'Locker', 'verbose_name_plural': 'Lockers'},
        ),
        migrations.AlterModelOptions(
            name='mae',
            options={'verbose_name': 'MAE', 'verbose_name_plural': 'MAE'},
        ),
        migrations.AlterModelOptions(
            name='perfiles',
            options={'verbose_name': 'Perfiles', 'verbose_name_plural': 'Perfiles'},
        ),
        migrations.AlterModelOptions(
            name='servicios',
            options={'verbose_name': 'Servicios', 'verbose_name_plural': 'Servicios'},
        ),
        migrations.AddField(
            model_name='areaservicio',
            name='descripcion',
            field=models.TextField(default='Sin info'),
        ),
    ]

# Generated by Django 4.2 on 2024-11-05 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_areaservicio_icono'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockers',
            name='genero',
            field=models.CharField(blank=True, choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='lockers',
            name='lugar_trabajo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.area'),
        ),
        migrations.AlterField(
            model_name='lockers',
            name='nombre_locker',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]

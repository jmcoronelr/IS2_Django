# Generated by Django 5.1 on 2024-09-04 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_permiso_rol_remove_usuario_roles_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='username',
            field=models.CharField(default='', max_length=150, unique=True),
        ),
    ]

# Generated by Django 5.1 on 2024-10-23 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_content_autor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='content',
            old_name='autor',
            new_name='author',
        ),
    ]

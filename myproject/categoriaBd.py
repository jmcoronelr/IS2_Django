import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from Categorias.models import Categorias

# Datos de las categorías
categorias_data = [
    {
        'descripcionCorta': 'N',
        'descripcionLarga': 'None',
        'estado': True,  # Por defecto activo, puedes ajustarlo
    },
]

for categoria_data in categorias_data:
    # Crear o actualizar la categoría
    categoria_obj, created = Categorias.objects.get_or_create(
        descripcionCorta=categoria_data['descripcionCorta'],
        defaults={
            'descripcionLarga': categoria_data['descripcionLarga'],
            'estado': categoria_data['estado']
        }
    )
    
    if created:
        print(f"Categoría creada: {categoria_obj.descripcionLarga}")
    else:
        # Si ya existe, actualizar valores
        categoria_obj.descripcionLarga = categoria_data['descripcionLarga']
        categoria_obj.estado = categoria_data['estado']
        categoria_obj.save()
        print(f"Categoría actualizada: {categoria_obj.descripcionLarga}")

from django.shortcuts import render, redirect
from django.urls import reverse
from content.models import Content  # Importa tu modelo de contenido

def home(request):
    # Filtra solo los contenidos que estén en estado 'published'
    contenidos = Content.objects.filter(status='published').order_by('created_at')

    # Si el usuario está autenticado, redirigir a la página del sistema
    if request.user.is_authenticated:
        return redirect('sistema')

    # Pasar los contenidos publicados al template 'home.html'
    return render(request, 'home.html', {'contenidos': contenidos})

def sistema(request):
    if not request.user.is_authenticated:
        return redirect('home')

    contenidos_publicados = Content.objects.filter(status='published')  # Aquí filtramos por estado
    return render(request, 'sistema.html', {'contenidos': contenidos_publicados})
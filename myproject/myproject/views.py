from django.shortcuts import render, redirect
from django.urls import reverse
from content.models import Content  # Importa tu modelo de contenido

def home(request):
    if request.user.is_authenticated:
        return redirect('sistema')
    return render(request, 'home.html')

def sistema(request):
    if not request.user.is_authenticated:
        return redirect('home')

    contenidos_publicados = Content.objects.filter(status='published')  # Aquí filtramos por estado
    return render(request, 'sistema.html', {'contenidos': contenidos_publicados})
from django.shortcuts import render, get_object_or_404
from content.models import Content
from .models import Historial

def historial_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    historial = Historial.objects.filter(content=content).order_by('-version')  # Ordenar por versiones

    return render(request, 'historial/historial_content.html', {
        'content': content,
        'historial': historial,
    })
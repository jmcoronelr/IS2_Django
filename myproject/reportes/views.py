from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse

def reportes_home(request):
    return render(request, 'reportes/reportes_home.html')

def reporte_likes_json(request):
    # Obtener todas las publicaciones ordenadas por número de likes, de mayor a menor
    contenidos = Content.objects.all().order_by('-likes')
    data = []

    # Construir la respuesta en formato JSON
    for contenido in contenidos:
        data.append({
            'title': contenido.title,
            'likes': contenido.likes,
        })
    
    return JsonResponse(data, safe=False)
from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, fields
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
def formatear_tiempo_revision(tiempo):
    """
    Formatea el tiempo de revisión para mostrarlo de manera legible.
    """
    total_segundos = int(tiempo.total_seconds())
    dias = total_segundos // 86400
    horas = (total_segundos % 86400) // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    # Construir la representación del tiempo formateado
    partes = []
    if dias > 0:
        partes.append(f"{dias}d")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    if segundos > 0 or not partes:  # Mostrar segundos si es que no hay ninguna otra parte
        partes.append(f"{segundos}s")
    
    return ' '.join(partes)

def reporte_revision_json(request):
    """
    Genera un reporte de tiempo de revisión para cada contenido que ha pasado por el estado de revisión.
    """
    contenidos = Content.objects.filter(
        revision_started_at__isnull=False,
        revision_ended_at__isnull=False
    ).annotate(
        tiempo_revision=ExpressionWrapper(
            F('revision_ended_at') - F('revision_started_at'),
            output_field=fields.DurationField()
        )
    ).order_by('-tiempo_revision')

    data = []
    for contenido in contenidos:
        tiempo_formateado = formatear_tiempo_revision(contenido.tiempo_revision)
        data.append({
            'title': contenido.title,
            'tiempo_revision': tiempo_formateado,
            'status': contenido.status,
        })

    return JsonResponse(data, safe=False)

def reporte_titulos_publicados_json(request):
    # Obtener solo los contenidos con estado 'publicado'
    contenidos = Content.objects.filter(status='published')
    data = []

    # Construir la respuesta en formato JSON con los títulos y fechas de publicación
    for contenido in contenidos:
        data.append({
            'title': contenido.title,
            'published_started_at': contenido.published_started_at.strftime('%Y-%m-%d') if contenido.published_started_at else None
        })
    
    return JsonResponse(data, safe=False)


def reporte_inactivos_json(request):
    """
    Genera un reporte de artículos inactivos con su título y fecha de inactivación.
    """
    contenidos = Content.objects.filter(status='inactive').annotate(
        fecha_inactivacion=F('inactivated_at')
    ).order_by('-fecha_inactivacion')

    data = []
    for contenido in contenidos:
        data.append({
            'title': contenido.title,
            'fecha_inactivacion': contenido.inactivated_at.strftime('%Y-%m-%d') if contenido.inactivated_at else None,
        })

    return JsonResponse(data, safe=False)

from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, fields
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils import timezone

# Función reutilizable para obtener y validar fechas
def obtener_fechas(request):
    """
    Obtiene y valida las fechas 'start_date' y 'end_date' de los parámetros de la solicitud.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP que contiene las fechas en sus parámetros.

    Returns:
        tuple: Tupla con las fechas inicial y final como objetos datetime. Si las fechas son inválidas, devuelve (None, None).
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if not start_date or not end_date:
            return None, None  # Fechas inválidas
        
        start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), timezone.get_current_timezone())
        end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()), timezone.get_current_timezone())
    else:
        start_date, end_date = None, None

    return start_date, end_date


def reportes_home(request):
    """
    Renderiza la página principal de reportes.

    Returns:
        HttpResponse: Respuesta con la plantilla renderizada 'reportes/reportes_home.html'.
    """
    return render(request, 'reportes/reportes_home.html')


def reporte_likes_json(request):
    """
    Genera un reporte en formato JSON de los contenidos ordenados por cantidad de likes.

    Returns:
        JsonResponse: Lista de contenidos con sus títulos y cantidad de likes.
    """
    start_date, end_date = obtener_fechas(request)
    
    if start_date and end_date:
        contenidos = Content.objects.filter(created_at__range=[start_date, end_date])
    else:
        contenidos = Content.objects.all()

    contenidos = contenidos.order_by('-likes')
    
    data = [{'title': contenido.title, 'likes': contenido.likes} for contenido in contenidos]
    
    return JsonResponse(data, safe=False)


def formatear_tiempo_revision(tiempo):
    """
    Formatea el tiempo de revisión para mostrarlo de manera legible.

    Args:
        tiempo (timedelta): Duración del tiempo de revisión.

    Returns:
        str: Tiempo formateado en días, horas, minutos y segundos.
    """
    if tiempo is None:
        return "N/A"
    
    total_segundos = int(tiempo.total_seconds())
    dias = total_segundos // 86400
    horas = (total_segundos % 86400) // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    partes = []
    if dias > 0:
        partes.append(f"{dias}d")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    if segundos > 0 or not partes:
        partes.append(f"{segundos}s")
    
    return ' '.join(partes)


def reporte_revision_json(request):
    """
    Genera un reporte en formato JSON de los tiempos de revisión de contenidos.

    Returns:
        JsonResponse: Lista de contenidos con título, tiempo de revisión formateado y estado.
    """
    start_date, end_date = obtener_fechas(request)
    
    if start_date and end_date:
        contenidos = Content.objects.filter(
            revision_started_at__isnull=False,
            revision_ended_at__isnull=False,
            revision_started_at__range=[start_date, end_date]
        )
    else:
        contenidos = Content.objects.filter(
            revision_started_at__isnull=False,
            revision_ended_at__isnull=False
        )
    
    contenidos = contenidos.annotate(
        tiempo_revision=ExpressionWrapper(
            F('revision_ended_at') - F('revision_started_at'),
            output_field=fields.DurationField()
        )
    ).order_by('-tiempo_revision')

    data = [{'title': contenido.title, 'tiempo_revision': formatear_tiempo_revision(contenido.tiempo_revision), 'status': contenido.status} for contenido in contenidos]

    return JsonResponse(data, safe=False)


def reporte_titulos_publicados_json(request):
    """
    Genera un reporte en formato JSON de los contenidos publicados.

    Returns:
        JsonResponse: Lista de contenidos con título y fecha de publicación.
    """
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        end_date = end_date + timedelta(days=1) - timedelta(seconds=1)
        contenidos = Content.objects.filter(status='published', published_started_at__range=[start_date, end_date])
    else:
        contenidos = Content.objects.filter(status='published')
    
    data = [{'title': contenido.title, 'published_started_at': contenido.published_started_at.strftime('%Y-%m-%d') if contenido.published_started_at else None} for contenido in contenidos]
    
    return JsonResponse(data, safe=False)


def reporte_visitas_json(request):
    """
    Genera un reporte en formato JSON de las visitas de contenidos publicados.

    Returns:
        JsonResponse: Lista de contenidos con título y cantidad de visitas.
    """
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        publicaciones = Content.objects.filter(status='published', created_at__range=[start_date, end_date]).order_by('-numero_visitas')
    else:
        publicaciones = Content.objects.filter(status='published').order_by('-numero_visitas')

    paginator = Paginator(publicaciones, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    data = [{'title': publicacion.title, 'visitas': publicacion.numero_visitas} for publicacion in page_obj]

    return JsonResponse(data, safe=False)


def reporte_most_shared_json(request):
    """
    Genera un reporte en formato JSON de los contenidos más compartidos.

    Returns:
        JsonResponse: Lista de contenidos con título y cantidad de veces compartido.
    """
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        contenidos = Content.objects.filter(created_at__range=[start_date, end_date]).order_by('-shared_count')
    else:
        contenidos = Content.objects.all().order_by('-shared_count')

    data = [{'title': contenido.title, 'shared_count': contenido.shared_count} for contenido in contenidos]

    return JsonResponse(data, safe=False)


def reporte_inactivos_json(request):
    """
    Genera un reporte en formato JSON de los contenidos inactivos.

    Returns:
        JsonResponse: Lista de contenidos con título y fecha de inactivación.
    """
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        contenidos = Content.objects.filter(
            status='inactive',
            inactivated_at__range=[start_date, end_date]
        )
    else:
        contenidos = Content.objects.filter(status='inactive')

    contenidos = contenidos.annotate(
        fecha_inactivacion=F('inactivated_at')
    ).order_by('-fecha_inactivacion')

    data = [{'title': contenido.title, 'fecha_inactivacion': contenido.inactivated_at.strftime('%Y-%m-%d') if contenido.inactivated_at else None} for contenido in contenidos]

    return JsonResponse(data, safe=False)

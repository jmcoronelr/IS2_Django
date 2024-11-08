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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if not start_date or not end_date:
            return None, None  # Fechas inválidas
        
        # Convertir las fechas a "aware" (conscientes de la zona horaria)
        start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), timezone.get_current_timezone())
        end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()), timezone.get_current_timezone())
    else:
        start_date, end_date = None, None

    return start_date, end_date



def reportes_home(request):
    return render(request, 'reportes/reportes_home.html')


def reporte_likes_json(request):
    # Obtener las fechas del request
    start_date, end_date = obtener_fechas(request)
    
    if start_date and end_date:
        # Filtrar contenidos dentro del rango de fechas
        contenidos = Content.objects.filter(created_at__range=[start_date, end_date])
    else:
        # Si no se proporcionan fechas, traer todos los contenidos
        contenidos = Content.objects.all()

    # Ordenar por likes
    contenidos = contenidos.order_by('-likes')
    
    data = []
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
    if tiempo is None:
        return "N/A"  # Manejo de posibles valores nulos
    
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
    if segundos > 0 or not partes:  # Mostrar segundos si no hay otra parte
        partes.append(f"{segundos}s")
    
    return ' '.join(partes)


def reporte_revision_json(request):
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
    
    # Calcular el tiempo de revisión
    contenidos = contenidos.annotate(
        tiempo_revision=ExpressionWrapper(
            F('revision_ended_at') - F('revision_started_at'),
            output_field=fields.DurationField()
        )
    ).order_by('-tiempo_revision')

    # Formatear los resultados para el JSON
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
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        # Incluir el rango completo del día hasta las 23:59:59 del día final
        end_date = end_date + timedelta(days=1) - timedelta(seconds=1)
        contenidos = Content.objects.filter(status='published', published_started_at__range=[start_date, end_date])
    else:
        contenidos = Content.objects.filter(status='published')
    
    data = []
    for contenido in contenidos:
        data.append({
            'title': contenido.title,
            'published_started_at': contenido.published_started_at.strftime('%Y-%m-%d') if contenido.published_started_at else None
        })
    
    return JsonResponse(data, safe=False)


def reporte_visitas_json(request):
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        publicaciones = Content.objects.filter(status='published', created_at__range=[start_date, end_date]).order_by('-numero_visitas')
    else:
        publicaciones = Content.objects.filter(status='published').order_by('-numero_visitas')

    # Paginación: 20 resultados por página
    paginator = Paginator(publicaciones, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    data = [
        {
            'title': publicacion.title,
            'visitas': publicacion.numero_visitas
        }
        for publicacion in page_obj
    ]

    return JsonResponse(data, safe=False)


def reporte_most_shared_json(request):
    start_date, end_date = obtener_fechas(request)

    if start_date and end_date:
        contenidos = Content.objects.filter(created_at__range=[start_date, end_date]).order_by('-shared_count')
    else:
        contenidos = Content.objects.all().order_by('-shared_count')

    data = [
        {
            'title': contenido.title,
            'shared_count': contenido.shared_count,
        }
        for contenido in contenidos
    ]

    return JsonResponse(data, safe=False)


def reporte_inactivos_json(request):
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

    data = []
    for contenido in contenidos:
        data.append({
            'title': contenido.title,
            'fecha_inactivacion': contenido.inactivated_at.strftime('%Y-%m-%d') if contenido.inactivated_at else None,
        })

    return JsonResponse(data, safe=False)

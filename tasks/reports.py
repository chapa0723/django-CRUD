"""
Vistas para generar reportes de tareas
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.text import slugify
from xhtml2pdf import pisa
from datetime import timedelta
from .models import Task
from .permissions import get_user_accessible_tasks
import os

@login_required
def report_all_tasks(request):
    """
    Reporte de TODAS las tareas, con filtro opcional de días
    por fecha de CREACIÓN.
    """
    try:
        # Si 'days' es 0 o no se provee, no se aplica filtro de fecha
        days = int(request.GET.get('days', 0))
    except ValueError:
        days = 0
            
    # 1. Obtener todas las tareas accesibles
    tasks = get_user_accessible_tasks(request.user)
    report_title = "Reporte de Todas las Tareas"

    # 2. Aplicar filtro de fecha si 'days' es mayor a 0
    if days > 0:
        start_date = timezone.now() - timedelta(days=days)
        tasks = tasks.filter(created__gte=start_date)
        report_title = f"Tareas Creadas en los Últimos {days} Días"
    
    context = {
        'tasks': tasks.order_by('-created'),
        'total': tasks.count(),
        'period_days': days,
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': report_title,
        'report_type': 'all_tasks'
    })


@login_required
def report_completed_tasks(request):
    """
    Reporte de tareas COMPLETADAS, con filtro opcional de días
    por fecha de COMPLETACIÓN.
    """
    try:
        days = int(request.GET.get('days', 0))
    except ValueError:
        days = 0
            
    tasks = get_user_accessible_tasks(request.user)
    
    # 1. Filtro base: Tareas completadas
    tasks = tasks.filter(datecompleted__isnull=False)
    report_title = "Reporte de Tareas Completadas"

    # 2. Aplicar filtro de fecha si 'days' es mayor a 0
    if days > 0:
        start_date = timezone.now() - timedelta(days=days)
        # Filtramos por la fecha en que se completaron
        tasks = tasks.filter(datecompleted__gte=start_date)
        report_title = f"Tareas Completadas en los Últimos {days} Días"
    
    context = {
        'tasks': tasks.order_by('-datecompleted'),
        'total': tasks.count(),
        'period_days': days,
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': report_title,
        'report_type': 'completed'
    })


@login_required
def report_pending_tasks(request):
    """
    Reporte de tareas PENDIENTES, con filtro opcional de días
    por fecha de CREACIÓN.
    """
    try:
        days = int(request.GET.get('days', 0))
    except ValueError:
        days = 0
            
    tasks = get_user_accessible_tasks(request.user)
    
    # 1. Filtro base: Tareas pendientes
    tasks = tasks.filter(datecompleted__isnull=True)
    report_title = "Reporte de Tareas Pendientes"

    # 2. Aplicar filtro de fecha si 'days' es mayor a 0
    if days > 0:
        start_date = timezone.now() - timedelta(days=days)
        # Filtramos por la fecha en que se crearon
        tasks = tasks.filter(created__gte=start_date)
        report_title = f"Tareas Pendientes (Creadas en los últimos {days} días)"
    
    context = {
        'tasks': tasks.order_by('-created'),
        'total': tasks.count(),
        'period_days': days,
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': report_title,
        'report_type': 'pending'
    })


@login_required
def report_important_tasks(request):
    """
    Reporte de tareas IMPORTANTES y PENDIENTES, con filtro
    opcional de días por fecha de CREACIÓN.
    """
    try:
        days = int(request.GET.get('days', 0))
    except ValueError:
        days = 0
            
    tasks = get_user_accessible_tasks(request.user)
    
    # 1. Filtro base: Tareas importantes Y pendientes
    tasks = tasks.filter(
        important=True,
        datecompleted__isnull=True
    )
    report_title = "Reporte de Tareas Importantes (Pendientes)"

    # 2. Aplicar filtro de fecha si 'days' es mayor a 0
    if days > 0:
        start_date = timezone.now() - timedelta(days=days)
        # Filtramos por la fecha en que se crearon
        tasks = tasks.filter(created__gte=start_date)
        report_title = f"Tareas Importantes (Pendientes, creadas en los últimos {days} días)"
    
    context = {
        'tasks': tasks.order_by('-created'),
        'total': tasks.count(),
        'period_days': days,
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': report_title,
        'report_type': 'important'
    })

@login_required
def task_reports(request):
    """
    Panel principal de reportes de tareas
    """
    context = {
        'total_tasks': 0,
        'completed_tasks': 0,
        'pending_tasks': 0,
        'important_tasks': 0,
        'tasks_by_status': [],
        'tasks_by_user': [],
        'tasks_by_importance': [],
        'recent_tasks': [],
        'oldest_tasks': [],
    }
    
    # Obtener todas las tareas accesibles del usuario
    all_tasks = get_user_accessible_tasks(request.user)
    
    # Estadísticas generales
    context['total_tasks'] = all_tasks.count()
    context['completed_tasks'] = all_tasks.filter(datecompleted__isnull=False).count()
    context['pending_tasks'] = all_tasks.filter(datecompleted__isnull=True).count()
    context['important_tasks'] = all_tasks.filter(important=True).count()
    
    # Tareas recientes (últimos 30 días)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    context['recent_tasks'] = all_tasks.filter(created__gte=thirty_days_ago).count()
    
    # Tareas más antiguas (más de 1 mes sin completar)
    context['oldest_tasks'] = all_tasks.filter(
        datecompleted__isnull=True,
        created__lt=thirty_days_ago
    ).count()
    
    # Agrupar por estado (completadas/pendientes)
    completed = all_tasks.filter(datecompleted__isnull=False).count()
    pending = all_tasks.filter(datecompleted__isnull=True).count()
    context['tasks_by_status'] = [
        {'status': 'Completadas', 'count': completed},
        {'status': 'Pendientes', 'count': pending},
    ]
    
    # Agrupar por importancia
    important = all_tasks.filter(important=True).count()
    not_important = all_tasks.filter(important=False).count()
    context['tasks_by_importance'] = [
        {'importance': 'Importantes', 'count': important},
        {'importance': 'No Importantes', 'count': not_important},
    ]
    
    # Agrupar por usuario (solo el usuario actual por ahora)
    context['tasks_by_user'] = [
        {'user': request.user.username, 'count': context['total_tasks']},
    ]
    
    return render(request, 'reports.html', context)


@login_required
def report_tasks_created_period(request):
    """
    Reporte de tareas creadas en un período específico
    """
    # Valores por defecto: últimos 30 días
    days = int(request.GET.get('days', 30))
    
    start_date = timezone.now() - timedelta(days=days)
    
    all_tasks = get_user_accessible_tasks(request.user)
    recent_tasks = all_tasks.filter(created__gte=start_date).order_by('-created')
    
    context = {
        'tasks': recent_tasks,
        'period_days': days,
        'start_date': start_date,
        'total': recent_tasks.count(),
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': f'Tareas Creadas en los Últimos {days} Días',
        'report_type': 'created'
    })


@login_required
def report_tasks_completed_period(request):
    """
    Reporte de tareas completadas en un período específico
    """
    # Valores por defecto: últimos 30 días
    days = int(request.GET.get('days', 30))
    
    start_date = timezone.now() - timedelta(days=days)
    
    all_tasks = get_user_accessible_tasks(request.user)
    completed_tasks = all_tasks.filter(
        datecompleted__gte=start_date,
        datecompleted__isnull=False
    ).order_by('-datecompleted')
    
    context = {
        'tasks': completed_tasks,
        'period_days': days,
        'start_date': start_date,
        'total': completed_tasks.count(),
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': f'Tareas Completadas en los Últimos {days} Días',
        'report_type': 'completed'
    })


@login_required
def report_tasks_by_user(request):
    """
    Reporte agrupando tareas por usuario
    """
    all_tasks = get_user_accessible_tasks(request.user)
    
    # Agrupar por usuario
    tasks_by_user = all_tasks.values('user__username').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(datecompleted__isnull=False)),
        pending=Count('id', filter=Q(datecompleted__isnull=True)),
        important=Count('id', filter=Q(important=True))
    ).order_by('-total')
    
    context = {
        'grouped_data': tasks_by_user,
        'total': all_tasks.count(),
    }
    
    return render(request, 'report_by_user.html', {
        'context': context,
        'report_title': 'Tareas Agrupadas por Usuario',
        'report_type': 'by_user'
    })


@login_required
def report_tasks_by_importance(request):
    """
    Reporte agrupando tareas por importancia
    """
    all_tasks = get_user_accessible_tasks(request.user)
    
    # Agrupar por importancia
    tasks_by_importance = all_tasks.values('important').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(datecompleted__isnull=False)),
        pending=Count('id', filter=Q(datecompleted__isnull=True))
    ).order_by('-important')
    
    # Agregar nombre descriptivo
    for item in tasks_by_importance:
        item['importance_name'] = 'Importante' if item['important'] else 'No Importante'
    
    context = {
        'grouped_data': tasks_by_importance,
        'total': all_tasks.count(),
    }
    
    return render(request, 'report_by_importance.html', {
        'context': context,
        'report_title': 'Tareas Agrupadas por Importancia',
        'report_type': 'by_importance'
    })


@login_required
def report_old_pending_tasks(request):
    """
    Reporte de tareas pendientes más antiguas
    """
    days = int(request.GET.get('days', 30))
    
    start_date = timezone.now() - timedelta(days=days)
    
    all_tasks = get_user_accessible_tasks(request.user)
    old_tasks = all_tasks.filter(
        datecompleted__isnull=True,
        created__lt=start_date
    ).order_by('created')
    
    context = {
        'tasks': old_tasks,
        'period_days': days,
        'total': old_tasks.count(),
    }
    
    return render(request, 'report_tasks_list.html', {
        'context': context,
        'report_title': f'Tareas Pendientes con Más de {days} Días',
        'report_type': 'old_pending'
    })

@login_required
def export_pdf_report(request):
    """
    Genera un PDF utilizando xhtml2pdf.
    Recibe parámetros GET: report_type y days.
    """
    # 1. Obtener parámetros de la URL
    report_type = request.GET.get('report_type', 'all_tasks')
    try:
        days = int(request.GET.get('days', 0))
    except ValueError:
        days = 0

    # 2. Lógica de Filtrado (Idéntica a tus vistas web)
    tasks = get_user_accessible_tasks(request.user)
    
    # Filtro por días (Fecha base)
    start_date = None
    if days > 0:
        start_date = timezone.now() - timedelta(days=days)

    report_title = "Reporte de Tareas"
    
    # --- Variables de filtro para el template PDF ---
    filter_status = None
    filter_important = None
    
    # Aplicar filtros según el tipo de reporte
    if report_type == 'completed':
        tasks = tasks.filter(datecompleted__isnull=False)
        if start_date: 
            tasks = tasks.filter(datecompleted__gte=start_date)
        report_title = "Reporte de Tareas Completadas"
        tasks = tasks.order_by('-datecompleted')
        filter_status = 'completed' # <--- Setear variable
        
    elif report_type == 'pending':
        tasks = tasks.filter(datecompleted__isnull=True)
        if start_date: 
            tasks = tasks.filter(created__gte=start_date)
        report_title = "Reporte de Tareas Pendientes"
        tasks = tasks.order_by('created')
        filter_status = 'pending' # <--- Setear variable

    elif report_type == 'important': # Es importante Y pendiente
        tasks = tasks.filter(important=True, datecompleted__isnull=True)
        if start_date: 
            tasks = tasks.filter(created__gte=start_date)
        report_title = "Reporte de Tareas Importantes (Pendientes)"
        tasks = tasks.order_by('-created')
        filter_status = 'pending' # <--- Sigue siendo pendiente
        filter_important = 'yes' # <--- Setear variable
        
    else: # 'all_tasks' por defecto
        if start_date: 
            tasks = tasks.filter(created__gte=start_date)
        report_title = "Reporte de Total de Tareas"
        tasks = tasks.order_by('-created')

# 3. CONSTRUCCIÓN DEL NOMBRE DEL ARCHIVO (¡NUEVO!)
    now = timezone.now()
    date_str = now.strftime("%Y%m%d_%H%M")
    
    # Limpia el título (ej: "Reporte de Tareas Pendientes" -> "reporte-de-tareas-pendientes")
    title_slug = slugify(report_title)
    
    # Nombre final del archivo:
    filename = f"{title_slug}_{date_str}.pdf"
    
    # 4. PREPARAR EL CONTEXTO FINAL (usando los nombres que el template PDF espera)
    context = {
        'tasks': tasks,
        'user': request.user,
        'report_title': report_title,
        
        # Variables específicas que la plantilla PDF espera:
        'filter_status': filter_status,
        'filter_important': filter_important,
        
        # El template PDF espera estas variables, aunque no tengamos el filtro de fecha completo
        'filter_date_from': start_date.strftime("%d/%m/%Y") if start_date else None,
        'filter_date_to': timezone.now().strftime("%d/%m/%Y"), # Asume que el rango es hasta hoy
    }

    # 5. Generar el PDF con xhtml2pdf
    template_path = 'report_pdf_print.html'
    response = HttpResponse(content_type='application/pdf')
    
    # Configuramos para que se descargue el archivo
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Cargar el template y renderizar con el contexto
    template = get_template(template_path)
    html = template.render(context)

    # Crear el PDF
    pisa_status = pisa.CreatePDF(
    html, 
    dest=response, 
    link_callback=link_callback
)

    if pisa_status.err:
        return HttpResponse('Ocurrió un error al generar el PDF <pre>' + html + '</pre>')
    
    return response

# ESTA FUNCIÓN LE DICE A xhtml2pdf DÓNDE ENCONTRAR LOS ARCHIVOS
def link_callback(uri, rel):
    """
    Convierte las rutas de recursos locales (como static y media)
    a rutas absolutas del sistema de archivos.
    """
    # 1. Rutas estáticas (CSS, JS, Imágenes del proyecto)
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
        # Fallback para desarrollo (si STATIC_ROOT no está configurado o no se ha hecho collectstatic)
        if not os.path.isfile(path):
            path = finders.find(uri.replace(settings.STATIC_URL, ""))
        return path
    
    # 2. Rutas de Media (Archivos subidos por el usuario)
    if uri.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

    return uri
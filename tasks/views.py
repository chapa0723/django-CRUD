from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from .models import Task, TaskPermission
from .forms import TaskForm
from .auth_forms import SignUpForm, SignInForm
from .permissions import user_has_permission, get_user_accessible_tasks

def signup(request):
    return redirect('signin')


@login_required
def tasks(request):
    # Obtener todas las tareas accesibles al usuario
    all_tasks = get_user_accessible_tasks(request.user)
    # Filtrar solo las pendientes
    tasks = all_tasks.filter(datecompleted__isnull=True)
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
def tasks_completed(request):
    # Obtener todas las tareas accesibles al usuario
    all_tasks = get_user_accessible_tasks(request.user)
    # Filtrar solo las completadas
    tasks = all_tasks.filter(datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {"tasks": tasks})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {"form": TaskForm, "error": "Error al crear la Tarea."})


def home(request):
    return render(request, 'home.html')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        form = SignInForm()
        return render(request, 'signin.html', {"form": form})
    else:
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tasks')
        
        # Si hay errores (incluyendo CAPTCHA)
        return render(request, 'signin.html', {"form": form})

@login_required
@user_has_permission('view')
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    # Verificar permisos de edición
    can_edit = task.has_permission(request.user, 'edit')
    
    if request.method == 'GET':
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task, 
            'form': form,
            'can_edit': can_edit
        })
    else:
        # Verificar que el usuario puede editar
        if not can_edit:
            from django.contrib import messages
            messages.error(request, 'No tienes permiso para editar esta tarea.')
            return redirect('task_detail', task_id=task_id)
        
        try:
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task, 
                'form': form, 
                'error': 'Error al actualizar la Tarea.',
                'can_edit': can_edit
            })

@login_required
@user_has_permission('edit')
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    # Solo el propietario puede eliminar (por seguridad)
    if task.user != request.user:
        from django.contrib import messages
        messages.error(request, 'Solo el propietario puede eliminar esta tarea.')
        return redirect('tasks')
    
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def tasks_details(request):
    """Vista para mostrar todas las tareas en formato detallado con tabla ordenable y filtros"""
    # Obtener todas las tareas accesibles al usuario
    all_tasks = get_user_accessible_tasks(request.user)
    
    # Obtener parámetros de filtrado
    filter_status = request.GET.get('status', '')
    filter_important = request.GET.get('important', '')
    filter_date_from = request.GET.get('date_from', '')
    filter_date_to = request.GET.get('date_to', '')
    
    # Aplicar filtros
    tasks = all_tasks
    
    if filter_status == 'completed':
        tasks = tasks.filter(datecompleted__isnull=False)
    elif filter_status == 'pending':
        tasks = tasks.filter(datecompleted__isnull=True)
    
    if filter_important == 'yes':
        tasks = tasks.filter(important=True)
    elif filter_important == 'no':
        tasks = tasks.filter(important=False)
    
    if filter_date_from:
        from django.utils.dateparse import parse_date
        date_from = parse_date(filter_date_from)
        if date_from:
            tasks = tasks.filter(created__gte=date_from)
    
    if filter_date_to:
        from django.utils.dateparse import parse_date
        date_to = parse_date(filter_date_to)
        if date_to:
            tasks = tasks.filter(created__lte=date_to)
    
    # Obtener parámetro de ordenamiento
    sort_by = request.GET.get('sort', 'created')
    sort_order = request.GET.get('order', 'desc')
    
    # Validar y aplicar ordenamiento
    valid_sort_fields = ['title', 'user__username', 'created', 'datecompleted', 'important']
    if sort_by in valid_sort_fields:
        if sort_order == 'asc':
            tasks = tasks.order_by(sort_by)
        else:
            tasks = tasks.order_by(f'-{sort_by}')
    else:
        # Ordenamiento por defecto
        tasks = tasks.order_by('-created')
    
    return render(request, 'tasks_details.html', {
        'tasks': tasks,
        'filter_status': filter_status,
        'filter_important': filter_important,
        'filter_date_from': filter_date_from,
        'filter_date_to': filter_date_to,
        'sort_by': sort_by,
        'sort_order': sort_order,
    })


@login_required
def tasks_details_pdf(request):
    """Vista para generar PDF del listado de tareas con los mismos filtros y ordenamiento"""
    # Obtener todas las tareas accesibles al usuario
    all_tasks = get_user_accessible_tasks(request.user)
    
    # Obtener parámetros de filtrado (mismo código que tasks_details)
    filter_status = request.GET.get('status', '')
    filter_important = request.GET.get('important', '')
    filter_date_from = request.GET.get('date_from', '')
    filter_date_to = request.GET.get('date_to', '')
    
    # Aplicar filtros
    tasks = all_tasks
    
    if filter_status == 'completed':
        tasks = tasks.filter(datecompleted__isnull=False)
    elif filter_status == 'pending':
        tasks = tasks.filter(datecompleted__isnull=True)
    
    if filter_important == 'yes':
        tasks = tasks.filter(important=True)
    elif filter_important == 'no':
        tasks = tasks.filter(important=False)
    
    if filter_date_from:
        from django.utils.dateparse import parse_date
        date_from = parse_date(filter_date_from)
        if date_from:
            tasks = tasks.filter(created__gte=date_from)
    
    if filter_date_to:
        from django.utils.dateparse import parse_date
        date_to = parse_date(filter_date_to)
        if date_to:
            tasks = tasks.filter(created__lte=date_to)
    
    # Obtener parámetro de ordenamiento
    sort_by = request.GET.get('sort', 'created')
    sort_order = request.GET.get('order', 'desc')
    
    # Validar y aplicar ordenamiento
    valid_sort_fields = ['title', 'user__username', 'created', 'datecompleted', 'important']
    if sort_by in valid_sort_fields:
        if sort_order == 'asc':
            tasks = tasks.order_by(sort_by)
        else:
            tasks = tasks.order_by(f'-{sort_by}')
    else:
        tasks = tasks.order_by('-created')
    
    # Generar PDF
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        from django.template import Context
        
        template = get_template('tasks_details_pdf.html')
        html = template.render({
            'tasks': tasks,
            'user': request.user,
            'filter_status': filter_status,
            'filter_important': filter_important,
            'filter_date_from': filter_date_from,
            'filter_date_to': filter_date_to,
        })
        
        result = BytesIO()
        pdf = pisa.CreatePDF(src=BytesIO(html.encode("UTF-8")), dest=result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"tareas_detalle_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse('Error al generar el PDF', status=500)
    except ImportError:
        # Si xhtml2pdf no está instalado, usar alternativa simple
        from django.template.loader import render_to_string
        html_content = render_to_string('tasks_details_pdf_simple.html', {
            'tasks': tasks,
            'user': request.user,
            'filter_status': filter_status,
            'filter_important': filter_important,
            'filter_date_from': filter_date_from,
            'filter_date_to': filter_date_to,
        })
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="tareas_detalle.html"'
        return response
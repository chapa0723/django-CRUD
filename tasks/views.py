from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
from .forms import TaskForm, TaskStatusOnlyForm
from .auth_forms import SignUpForm, SignInForm

from .permissions import user_has_permission, get_user_accessible_tasks, get_user_role

from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.core.exceptions import PermissionDenied
from .mixins import RoleRequiredMixin
from .models import Task
from .forms import TaskStatusOnlyForm 
from .permissions import get_user_accessible_tasks
from .forms import TaskForm

def signup(request):
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'signup.html', {"form": form})
    else:
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signup.html', {"form": form})


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


# @login_required
# def create_task(request):
#     if request.method == "GET":
#         return render(request, 'create_task.html', {"form": TaskForm})
#     else:
#         try:
#             form = TaskForm(request.POST)
#             new_task = form.save(commit=False)
#             new_task.user = request.user
#             new_task.save()
#             return redirect('tasks')
#         except ValueError:
#             return render(request, 'create_task.html', {"form": TaskForm, "error": "Error al crear la Tarea."})

@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            
            if form.is_valid(): # Agregamos la validación del formulario
                new_task = form.save(commit=False)
                new_task.user = request.user
                
                # 🚨 LA CORRECCIÓN CRÍTICA: Asignación por defecto
                # Si el formulario no proporcionó un usuario asignado, se asigna al creador.
                if not new_task.assigned_user:
                    new_task.assigned_user = request.user 
                    
                new_task.save()
                return redirect('tasks')
            else:
                 # Si la validación del formulario falla (ej: campo requerido vacío)
                 return render(request, 'create_task.html', {"form": form, "error": "Error de validación al crear la Tarea. Revisa los campos."})
                 
        except ValueError:
            # Aquí manejas errores de tipo (ej: si se envía un valor no válido para un campo)
            return render(request, 'create_task.html', {"form": TaskForm(request.POST), "error": "Error al crear la Tarea."})


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

# @login_required
# @user_has_permission('view')
# def task_detail(request, task_id):
#     task = get_object_or_404(Task, pk=task_id)
    
#     # Verificar permisos de edición
#     can_edit = task.has_permission(request.user, 'edit')
    
#     if request.method == 'GET':
#         form = TaskForm(instance=task)
#         return render(request, 'task_detail.html', {
#             'task': task, 
#             'form': form,
#             'can_edit': can_edit
#         })
#     else:
#         # Verificar que el usuario puede editar
#         if not can_edit:
#             from django.contrib import messages
#             messages.error(request, 'No tienes permiso para editar esta tarea.')
#             return redirect('task_detail', task_id=task_id)
        
#         try:
#             form = TaskForm(request.POST, instance=task)
#             form.save()
#             return redirect('tasks')
#         except ValueError:
#             return render(request, 'task_detail.html', {
#                 'task': task, 
#                 'form': form, 
#                 'error': 'Error al actualizar la Tarea.',
#                 'can_edit': can_edit
#             })


@login_required
@user_has_permission('view')
def task_detail(request, task_id):
    # El decorador @user_has_permission ya verifica si el usuario puede ver la tarea
    # y redirige si no tiene permiso.
    task = get_object_or_404(Task, pk=task_id)
    
    # 1. Chequeo de Roles y Permisos
    can_edit = task.has_permission(request.user, 'edit')
    current_role = get_user_role(request.user) # Obtenemos el rol para la lógica del formulario

    # 2. Definir qué Formulario Usar (Lógica de Roles)
    is_admin_or_soporte = request.user.is_superuser or \
                          current_role in ['Administrador', 'Soporte Técnico']
    
    is_ventas_only = (current_role == 'Ventas' and not is_admin_or_soporte) # Evita multi-grupo

    # Seleccionar la clase de formulario
    if is_ventas_only:
        FormClass = TaskStatusOnlyForm
    else:
        FormClass = TaskForm


    if request.method == 'GET':
        # Renderiza el formulario con la clase seleccionada
        form = FormClass(instance=task) 
        
        # Agregamos la variable is_admin para el botón Eliminar
        is_admin = current_role == 'Administrador' or request.user.is_superuser
        
        #Lógica para el botón "Marcar como Completada"
        is_pending = task.datecompleted is None
        
        #Lógica para el botón "Eliminar" (para el template)
        is_admin = request.user.groups.filter(name='Administrador').exists()
        
        if request.method == 'GET':
        # Mantenemos la instancia del formulario (FormClass) en la vista
        # para que el bloque POST sepa qué campos puede validar.
        # No importa que no se muestre en el template.
            form = FormClass(instance=task)

        return render(request, 'task_detail.html', {
            'task': task, 
            'form': form,
            'can_edit': can_edit,
            'is_pending': is_pending,
            'is_admin': is_admin, # <-- Variable para mostrar/ocultar el botón "Eliminar"
            'current_role': current_role, # <-- Variable opcional para debug/display
            'is_superuser': request.user.is_superuser,
        })
    
    else: # request.method == 'POST'
        # 3. Bloque POST (Edición)
        if not can_edit:
            # Aunque ya se checó en el GET, se vuelve a checar por seguridad de POST
            messages.error(request, 'No tienes permiso para editar esta tarea.')
            return redirect('task_detail', task_id=task_id)
        
        # Procesar con el formulario correcto (FormClass)
        form = FormClass(request.POST, instance=task)
        
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Tarea actualizada con éxito.')
            return redirect('tasks')
        
        else:
            # Retorna el formulario con los errores si falla la validación
            messages.error(request, 'Error al actualizar la Tarea. Revisa los campos.')
            return render(request, 'task_detail.html', {
                'task': task, 
                'form': form, 
                'can_edit': can_edit
                # No es necesario pasar 'error', los errores están en form.errors
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


@login_required
def task_list(request):
    # 🚨 FIX DE VISIBILIDAD 🚨
    # Solo se muestran las tareas que el usuario tiene derecho a ver
    tasks = get_user_accessible_tasks(request.user).order_by('-created')
    
    return render(request, 'tasks.html', {'tasks': tasks})


class TaskEditView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Task
    
    # 1. Grupos permitidos para acceder a esta vista (el mixin lo verifica)
    allowed_groups = ['Soporte Técnico', 'Ventas'] 

    # 2. Formulario estándar (para Administradores y Soporte Técnico)
    form_class = TaskForm 
    
    # 3. Formulario restringido (para Ventas)
    ventas_form_class = TaskStatusOnlyForm
    
    template_name = 'task_edit.html'
    success_url = reverse_lazy('tasks')

    # A. Sobreescribir qué tareas puede ver/editar
    def get_queryset(self):
        
        # 1. SIEMPRE DEVOLVER todo para roles de alto nivel.
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Administrador').exists():
            # Forzamos a devolver el QuerySet completo del modelo, 
            # eliminando cualquier filtro que pudiera estar aplicándose.
            return self.model.objects.all() 

        # 2. Para roles intermedios, aplicamos el filtro estricto.
        from .permissions import get_user_accessible_tasks
        accessible_tasks = get_user_accessible_tasks(self.request.user)
        
        # Filtrar el modelo base para que solo contenga IDs de tareas accesibles.
        return self.model.objects.filter(id__in=accessible_tasks.values_list('id', flat=True))

    # B. Sobreescribir qué formulario usar (Esta parte es correcta)
    def get_form_class(self):
        """Selecciona el formulario basado en el rol, priorizando la restricción."""
        
        # Si el usuario pertenece SOLAMENTE al grupo 'Ventas'
        is_ventas_only = self.request.user.groups.filter(name='Ventas').exists() and \
                         not self.request.user.groups.filter(name='Soporte Técnico').exists() and \
                         not self.request.user.groups.filter(name='Administrador').exists()
        
        if is_ventas_only:
            return self.ventas_form_class
        
        # Si es Administrador, Soporte Técnico, o un Ventas con más privilegios, usa el formulario completo
        return self.form_class


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('tasks')
    template_name = 'task_confirm_delete.html' # Crea este template simple

    def dispatch(self, request, *args, **kwargs):
        # 1. Chequeo de Permiso: Solo Superuser o Administrador
        is_allowed_to_delete = request.user.is_superuser or \
                               request.user.groups.filter(name='Administrador').exists()
        
        if not is_allowed_to_delete:
            # Niega el acceso si no tiene el rol de Administrador/Superusuario
            raise PermissionDenied("No tienes permiso para eliminar tareas.")
            
        return super().dispatch(request, *args, **kwargs)

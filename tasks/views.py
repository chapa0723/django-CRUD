from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task, TaskPermission
from .forms import TaskForm
from .auth_forms import SignUpForm, SignInForm
from .permissions import user_has_permission, get_user_accessible_tasks

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
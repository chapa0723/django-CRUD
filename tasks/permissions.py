"""
Utilidades para manejo de permisos en las tareas
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from functools import wraps
from .models import Task, TaskPermission


def user_has_permission(permission_type='view'):
    """
    Decorador para verificar que un usuario tiene permiso sobre una tarea
    
    Uso:
        @user_has_permission('edit')
        def my_view(request, task_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            task_id = kwargs.get('task_id')
            
            if not task_id:
                raise PermissionDenied("No se proporcionó ID de tarea")
            
            task = get_object_or_404(Task, pk=task_id)
            
            # Verificar permiso
            if not task.has_permission(request.user, permission_type):
                messages.error(
                    request, 
                    f"No tienes permiso para {permission_type} esta tarea."
                )
                return redirect('tasks')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# def get_user_accessible_tasks(user):
#     """
#     Retorna todas las tareas a las que un usuario tiene acceso
    
#     Incluye:
#     - Tareas propias del usuario
#     - Tareas compartidas con permisos
#     """
#     # Tareas propias
#     owned_tasks = Task.objects.filter(user=user)
    
#     # Tareas compartidas con el usuario
#     shared_task_ids = TaskPermission.objects.filter(user=user).values_list('task_id', flat=True)
#     shared_tasks = Task.objects.filter(id__in=shared_task_ids)
    
#     # Combinar y retornar
#     return owned_tasks | shared_tasks

def get_user_accessible_tasks(user):
    # Regla 1: Superusuario / Administrador siempre ven todo
    if user.is_superuser or user.groups.filter(name='Administrador').exists():
        return Task.objects.all()

    # Regla 2: Usuario es propietario (user)
    q_filter = Q(user=user) | Q(assigned_user=user)
    
    # Regla 3: Tareas compartidas por TaskPermission
    q_filter |= Q(task_permissions__user=user)
    
    # Regla 4: Visibilidad del Rol Ventas/Soporte
    if user.groups.filter(name__in=['Ventas', 'Soporte Técnico']).exists():
        # Ver tareas que le pertenecen, O las que tiene asignadas, O las compartidas.
        
        if user.groups.filter(name='Ventas').exists():
            # Ventas tiene permiso especial para ver tareas sin asignar (null)
            q_filter |= Q(assigned_user__isnull=True)
            
    # Filtra las tareas de todos los orígenes de permiso
    return Task.objects.filter(q_filter).distinct()


def can_share_task(user, task):
    """
    Verifica si un usuario puede compartir una tarea (debe ser el propietario)
    """
    return task.user == user


def share_task(task, user, can_edit=False, can_delete=False, granted_by=None):
    """
    Comparte una tarea con un usuario otorgándole permisos específicos
    
    Args:
        task: La tarea a compartir
        user: El usuario con quien compartir
        can_edit: Si el usuario puede editar
        can_delete: Si el usuario puede eliminar
        granted_by: El usuario que está otorgando el permiso
    """
    if user == task.user:
        raise ValueError("No puedes compartir una tarea contigo mismo")
    
    permission, created = TaskPermission.objects.get_or_create(
        task=task,
        user=user,
        defaults={
            'can_view': True,
            'can_edit': can_edit,
            'can_delete': can_delete,
            'granted_by': granted_by or task.user,
        }
    )
    
    if not created:
        permission.can_view = True
        permission.can_edit = can_edit
        permission.can_delete = can_delete
        permission.granted_by = granted_by or task.user
        permission.save()
    
    return permission

def get_user_role(user):
    """Devuelve el nombre del grupo al que pertenece un usuario."""
    if user.is_superuser:
        return "Desarrollador"
    
    # Intenta obtener el primer grupo al que pertenece
    try:
        group = user.groups.all().first()
        return group.name
    except AttributeError:
        # El usuario no tiene grupos asignados (aunque esté logueado)
        return "Sin Rol"

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(max_length=1000)
  created = models.DateTimeField(auto_now_add=True)
  datecompleted = models.DateTimeField(null=True, blank=True)
  important = models.BooleanField(default=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tasks')
  assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Si el empleado se va, no borra la tarea
        null=True, 
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Usuario Asignado'
    )

  class Meta:
    verbose_name = 'Tarea'
    verbose_name_plural = 'Tareas'
    ordering = ['-created']

  def __str__(self):
    return self.title + ' - ' + self.user.username
  
  def has_permission(self, user, permission_type='view'):
    """Verifica si un usuario tiene permiso sobre esta tarea"""
    
    # 🚨 FIX CRÍTICO: El Administrador/Superusuario tiene permiso total
    if user.is_superuser or user.groups.filter(name='Administrador').exists():
        return True
    
    # 1. El propietario tiene todos los permisos
    if user == self.user:
      return True
    
    # 2. Verificar permisos explícitos de TaskPermission
    if permission_type == 'edit':
      return TaskPermission.objects.filter(
        task=self, 
        user=user, 
        can_edit=True
      ).exists()
    
    elif permission_type == 'view':
      return TaskPermission.objects.filter(
        task=self, 
        user=user
      ).exists()
    
    return False
  
  # def has_permission(self, user, permission_type='view'):
  #   """Verifica si un usuario tiene permiso sobre esta tarea"""
  #   # El propietario tiene todos los permisos
  #   if user == self.user:
  #     return True
    
  #   # Verificar permisos explícitos
  #   if permission_type == 'edit':
  #     return TaskPermission.objects.filter(
  #       task=self, 
  #       user=user, 
  #       can_edit=True
  #     ).exists()
    
  #   elif permission_type == 'view':
  #     return TaskPermission.objects.filter(
  #       task=self, 
  #       user=user
  #     ).exists()
    
  #   return False


class TaskPermission(models.Model):
  """Modelo para gestionar permisos de usuarios sobre tareas específicas"""
  
  PERMISSION_CHOICES = [
    ('view', 'Ver'),
    ('edit', 'Editar'),
    ('delete', 'Eliminar'),
  ]
  
  task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_permissions')
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_permissions')
  can_view = models.BooleanField(default=True, verbose_name='Puede Ver')
  can_edit = models.BooleanField(default=False, verbose_name='Puede Editar')
  can_delete = models.BooleanField(default=False, verbose_name='Puede Eliminar')
  granted_at = models.DateTimeField(auto_now_add=True)
  granted_by = models.ForeignKey(
    User, 
    on_delete=models.SET_NULL, 
    null=True, 
    related_name='granted_permissions',
    verbose_name='Concedido por'
  )
  
  class Meta:
    verbose_name = 'Permiso de Tarea'
    verbose_name_plural = 'Permisos de Tareas'
    unique_together = ['task', 'user']
  
  def __str__(self):
    return f'{self.user.username} - {self.task.title}'

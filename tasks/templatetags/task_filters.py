from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter
def get_user_role(user):
    """
    Retorna el nombre del rol (grupo) de un usuario.
    Maneja Superusuarios y usuarios sin grupo asignado.
    """
    if not user:
        return "N/A"
        
    if user.is_superuser:
        return "Desarrollador"
    
    # Tarea: Verificar si el usuario es Superusuario y Administrador al mismo tiempo
    if user.groups.filter(name='Administrador').exists():
        return "Administrador"

    # Obtiene el primer grupo (rol) al que pertenece
    group = user.groups.first() 
    return group.name if group else "Sin Rol"
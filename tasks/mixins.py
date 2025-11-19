from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(AccessMixin):
    # Grupos permitidos para acceder a esta vista 
    allowed_groups = [] 
    
    def dispatch(self, request, *args, **kwargs):
        # 1. Si no está autenticado, maneja el permiso (ej: va a login)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 2. Si es Desarrollador (Superuser) o Administrador, le damos acceso total
        is_admin_or_dev = request.user.is_superuser or \
                          request.user.groups.filter(name='Administrador').exists()
        
        if is_admin_or_dev:
            return super().dispatch(request, *args, **kwargs)

        # 3. Verifica si pertenece a alguno de los grupos permitidos
        if not any(request.user.groups.filter(name=group).exists() for group in self.allowed_groups):
            raise PermissionDenied # Lanza error 403 si no tiene permiso
            
        return super().dispatch(request, *args, **kwargs)
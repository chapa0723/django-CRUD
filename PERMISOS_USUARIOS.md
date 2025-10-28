# Sistema de Gestión de Usuarios y Permisos

## Resumen de Cambios

Se ha implementado un sistema completo de gestión de usuarios y permisos para las tareas.

## Nuevos Modelos

### 1. UserProfile (app: users)
Extiende el modelo User de Django con información adicional:
- `bio`: Biografía del usuario
- `location`: Ubicación
- `birth_date`: Fecha de nacimiento
- `phone`: Teléfono
- `created_at`: Fecha de creación
- `updated_at`: Fecha de actualización

El perfil se crea automáticamente cuando se crea un usuario.

### 2. TaskPermission (app: tasks)
Gestiona permisos específicos sobre tareas individuales:
- `task`: La tarea sobre la que se otorga el permiso
- `user`: El usuario que recibe el permiso
- `can_view`: Permiso para ver la tarea
- `can_edit`: Permiso para editar la tarea
- `can_delete`: Permiso para eliminar la tarea
- `granted_at`: Fecha en que se otorgó el permiso
- `granted_by`: Usuario que otorgó el permiso

## Funcionalidades

### Permisos en Tareas

El modelo `Task` ahora tiene métodos para verificar permisos:

```python
# Verificar si un usuario tiene permiso
task.has_permission(user, permission_type='view')  # 'view' o 'edit'
```

### Decoradores

Se creó el decorador `@user_has_permission()` para proteger vistas:

```python
from tasks.permissions import user_has_permission

@login_required
@user_has_permission('edit')
def my_view(request, task_id):
    # Solo usuarios con permiso de edición pueden acceder
    ...
```

### Utilidades

- `get_user_accessible_tasks(user)`: Retorna todas las tareas accesibles al usuario (propias + compartidas)
- `can_share_task(user, task)`: Verifica si un usuario puede compartir una tarea
- `share_task(task, user, can_edit=False, can_delete=False)`: Comparte una tarea con un usuario

## Cambios en las Vistas

Las vistas ahora verifican permisos adecuadamente:

- **tasks()**: Muestra tareas propias + tareas compartidas
- **tasks_completed()**: Muestra tareas completadas (propias + compartidas)
- **task_detail()**: Requiere permiso de vista; si puede editar depende de permisos
- **complete_task()**: Requiere permiso de edición
- **delete_task()**: Solo el propietario puede eliminar

## Configuración de Admin

Los modelos han sido registrados en Django Admin con configuraciones optimizadas:

- **Task**: Filtros por importancia, fechas; búsqueda por título, descripción, usuario
- **TaskPermission**: Filtros por tipo de permisos; búsqueda por tarea y usuario
- **UserProfile**: Listado y búsqueda por usuario, ubicación, teléfono

## Aplicar Migraciones

Para aplicar los cambios a la base de datos, ejecuta:

```bash
python manage.py migrate
```

Esto creará las tablas necesarias:
- `users_userprofile`
- `tasks_taskpermission`
- Actualizará `tasks_task` con el nuevo related_name

## Uso del Sistema

### Para Desarrolladores

1. **Compartir una tarea**:
```python
from tasks.permissions import share_task

# Compartir con permiso de solo lectura
share_task(task, user, can_edit=False)

# Compartir con permiso de edición
share_task(task, user, can_edit=True)
```

2. **Verificar permisos en vistas**:
```python
from tasks.permissions import user_has_permission

@login_required
@user_has_permission('view')
def view_task(request, task_id):
    ...
```

3. **Obtener tareas accesibles**:
```python
from tasks.permissions import get_user_accessible_tasks

user_tasks = get_user_accessible_tasks(request.user)
```

### Para Usuarios (TBD - Futuras Funcionalidades)

El sistema está preparado para que en el futuro se puedan agregar:
- Interfaz para compartir tareas con otros usuarios
- Listado de tareas compartidas
- Gestión de permisos desde la interfaz de usuario

## Cambios Realizados

1. ✅ Corrección de errores de sintaxis en `settings.py` y `users/models.py`
2. ✅ Creación del modelo `TaskPermission`
3. ✅ Creación del decorador y utilidades de permisos
4. ✅ Actualización de vistas para usar el sistema de permisos
5. ✅ Registro de modelos en Django Admin
6. ✅ Creación de migraciones

## Próximos Pasos Recomendados

1. Ejecutar las migraciones: `python manage.py migrate`
2. Probar el sistema con usuarios de prueba
3. (Opcional) Agregar interfaz de usuario para compartir tareas
4. (Opcional) Agregar notificaciones cuando se comparte una tarea
5. (Opcional) Crear vistas de gestión de permisos en Django Admin


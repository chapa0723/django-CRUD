from django.contrib import admin
from .models import Task, TaskPermission

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
  list_display = ('title', 'user', 'important', 'created', 'datecompleted')
  list_filter = ('important', 'created', 'datecompleted')
  search_fields = ('title', 'description', 'user__username')
  readonly_fields = ('created', )
  fieldsets = (
    ('Información General', {
      'fields': ('title', 'description', 'user', 'important')
    }),
    ('Fechas', {
      'fields': ('created', 'datecompleted')
    }),
  )

class TaskPermissionAdmin(admin.ModelAdmin):
  list_display = ('task', 'user', 'can_view', 'can_edit', 'can_delete', 'granted_at', 'granted_by')
  list_filter = ('can_view', 'can_edit', 'can_delete', 'granted_at')
  search_fields = ('task__title', 'user__username')
  readonly_fields = ('granted_at', )

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskPermission, TaskPermissionAdmin)
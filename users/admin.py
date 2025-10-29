from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
  list_display = ('user', 'location', 'phone', 'created_at')
  list_filter = ('location', 'created_at')
  search_fields = ('user__username', 'user__email', 'location', 'phone')
  readonly_fields = ('created_at', 'updated_at')

admin.site.register(UserProfile, UserProfileAdmin)

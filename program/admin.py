from django.contrib import admin
from .models import Theme, Session, SessionReflection

# Register your models here.
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'is_free_trial', 'is_authenticate', 'created_at')
    list_filter = ('is_free_trial', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'theme', 'order', 'created_at')
    list_filter = ('theme', 'created_at')
    search_fields = ('title', 'subtitle', 'text_content')
    ordering = ('theme', 'order', 'created_at')

class SessionReflectionAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'session', 'initial_intensity_level', 'final_intensity_level', 'created_at')
    list_filter = ('session', 'created_at')
    search_fields = ('user__username', 'session__title', 'initial_thoughts', 'final_thoughts')
    ordering = ('-created_at',)

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(SessionReflection, SessionReflectionAdmin)

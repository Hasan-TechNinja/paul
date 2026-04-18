from django.contrib import admin
from .models import Theme, Session, SessionReflection, ThemeTranslation, SessionTranslation

# Register your models here.

class ThemeTranslationInline(admin.TabularInline):
    model = ThemeTranslation
    extra = 0

class SessionTranslationInline(admin.TabularInline):
    model = SessionTranslation
    extra = 0

class SessionInline(admin.StackedInline):
    model = Session
    extra = 1

class ThemeAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'is_free_trial', 'is_authenticate', 'voice_id', 'session_key', 'created_at')
    list_filter = ('is_free_trial', 'created_at')
    search_fields = ('title', 'description')
    inlines = [SessionInline, ThemeTranslationInline]
    ordering = ('-created_at',)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'theme', 'get_session_key', 'order', 'created_at')
    list_filter = ('theme', 'created_at')
    search_fields = ('title', 'subtitle', 'text_content')
    inlines = [SessionTranslationInline]
    ordering = ('theme', 'order', 'created_at')

    def get_session_key(self, obj):
        return obj.theme.session_key if obj.theme else None
    get_session_key.short_description = 'Session Key'
    get_session_key.admin_order_field = 'theme__session_key'

class SessionReflectionAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'session', 'see_intensity_level', 'feel_intensity_level', 'created_at')
    list_filter = ('session', 'created_at')
    search_fields = ('user__username', 'session__title', 'see_thoughts', 'feel_thoughts')
    readonly_fields = ('user', 'session')
    ordering = ('-created_at',)

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(SessionReflection, SessionReflectionAdmin)
admin.site.register(ThemeTranslation)
admin.site.register(SessionTranslation)

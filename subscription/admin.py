from django.contrib import admin
from .models import Plan, UserSubscription, ThemeSubscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'interval', 'duration_days')
    list_filter = ('plan_type', 'interval')
    search_fields = ('name',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('is_active', 'plan')
    readonly_fields = ('start_date',)


@admin.register(ThemeSubscription)
class ThemeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'plan', 'is_active', 'start_date', 'end_date', 'purchased_at')
    search_fields = ('user__email', 'theme__title', 'plan__name')
    list_filter = ('is_active', 'plan', 'theme')
    readonly_fields = ('purchased_at',)

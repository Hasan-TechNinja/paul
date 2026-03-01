from django.contrib import admin
from .models import Plan, UserSubscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'interval')
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('is_active', 'plan')

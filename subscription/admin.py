from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
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
    readonly_fields = ('start_date', 'end_date', 'purchased_at')
    fields = ('user', 'plan', 'theme', 'is_active', 'start_date', 'end_date', 'purchased_at')

    class Media:
        js = ('admin/js/theme_subscription.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'plan-types/',
                self.admin_site.admin_view(self.plan_types_json),
                name='subscription_plan_types',
            ),
        ]
        # Prepend so our URL takes priority
        return custom_urls + urls

    def plan_types_json(self, request):
        """
        Returns a JSON mapping of plan IDs to their plan_type.
        Used by theme_subscription.js to determine which plans are 'pro'
        without relying on text matching.

        Response format:
        {
            "pro_plan_ids": [1, 3, ...],
            "plans": {"1": "pro", "2": "basic", ...}
        }
        """
        plans = Plan.objects.only('id', 'plan_type')
        pro_ids = []
        all_plans = {}
        for plan in plans:
            all_plans[str(plan.id)] = plan.plan_type
            if plan.plan_type == 'pro':
                pro_ids.append(plan.id)
        return JsonResponse({'pro_plan_ids': pro_ids, 'plans': all_plans})

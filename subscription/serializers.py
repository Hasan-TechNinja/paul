from rest_framework import serializers
from django.utils import timezone
from .models import Plan, UserSubscription, ThemeSubscription
from program.models import Theme


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'plan_type', 'price', 'interval', 'duration_days', 'features']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    is_pro_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'start_date', 'end_date', 'is_active', 'is_pro_active']

    def get_is_pro_active(self, obj):
        return obj.is_pro_active


class ThemeSubscriptionSerializer(serializers.ModelSerializer):
    theme_id = serializers.IntegerField(source='theme.id', read_only=True)
    theme_title = serializers.CharField(source='theme.title', read_only=True)
    plan = PlanSerializer(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = ThemeSubscription
        fields = [
            'id', 'theme_id', 'theme_title', 'plan',
            'start_date', 'end_date', 'is_active',
            'days_remaining', 'purchased_at',
        ]


# --- Input serializers ---

class ProSubscribeSerializer(serializers.Serializer):
    """Purchase a Pro plan (unlocks all themes)."""
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            plan = Plan.objects.get(id=value)
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan not found.")
        if plan.plan_type != 'pro':
            raise serializers.ValidationError("This plan is not a Pro plan.")
        return value


class BasicThemePurchaseSerializer(serializers.Serializer):
    """Purchase one or more themes under a Basic plan."""
    plan_id = serializers.IntegerField()
    theme_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of Theme IDs to purchase."
    )

    def validate_plan_id(self, value):
        try:
            plan = Plan.objects.get(id=value)
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan not found.")
        if plan.plan_type != 'basic':
            raise serializers.ValidationError("This plan is not a Basic plan. Use the Pro subscribe endpoint.")
        return value

    def validate_theme_ids(self, value):
        existing_ids = set(Theme.objects.filter(id__in=value).values_list('id', flat=True))
        missing = set(value) - existing_ids
        if missing:
            raise serializers.ValidationError(f"Theme(s) not found: {sorted(missing)}")
        return list(set(value))  # deduplicate

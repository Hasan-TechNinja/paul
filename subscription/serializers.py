from rest_framework import serializers
from .models import Plan, UserSubscription

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'interval', 'features']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active']

class SubscribeSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

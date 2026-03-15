from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from .models import Plan, UserSubscription, ThemeSubscription
from .serializers import (
    PlanSerializer,
    UserSubscriptionSerializer,
    ThemeSubscriptionSerializer,
    ProSubscribeSerializer,
    BasicThemePurchaseSerializer,
)


class PlanListView(generics.ListAPIView):
    """List all available plans (public)."""
    queryset = Plan.objects.all().order_by('plan_type', 'price')
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class CurrentSubscriptionView(APIView):
    """
    GET: Returns the user's current Pro subscription status
    and all active per-theme (Basic) subscriptions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Pro subscription
        pro_sub, _ = UserSubscription.objects.get_or_create(user=user)
        pro_sub.check_and_update_status()

        # Basic per-theme subscriptions (only active ones, auto-expire stale)
        theme_subs = ThemeSubscription.objects.filter(user=user, is_active=True).select_related('theme', 'plan')
        for ts in theme_subs:
            ts.check_and_update_status()

        # Re-fetch after potential status updates
        active_theme_subs = ThemeSubscription.objects.filter(user=user, is_active=True).select_related('theme', 'plan')

        return Response({
            'pro_subscription': UserSubscriptionSerializer(pro_sub).data,
            'is_pro_active': pro_sub.is_pro_active,
            'theme_subscriptions': ThemeSubscriptionSerializer(active_theme_subs, many=True).data,
        })


class ProSubscribeView(APIView):
    """
    POST: Purchase a Pro plan — unlocks ALL themes for the plan duration.
    Body: { "plan_id": <int> }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ProSubscribeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        now = timezone.now()
        end_date = now + timedelta(days=plan.duration_days)

        user_sub, _ = UserSubscription.objects.get_or_create(user=request.user)
        user_sub.plan = plan
        user_sub.start_date = now
        user_sub.end_date = end_date
        user_sub.is_active = True
        user_sub.save()

        return Response({
            'message': f'Successfully subscribed to {plan.name}. All themes unlocked until {end_date:%Y-%m-%d}.',
            'subscription': UserSubscriptionSerializer(user_sub).data,
        }, status=status.HTTP_200_OK)


class BasicThemePurchaseView(APIView):
    """
    POST: Purchase one or more themes under a Basic plan.
    Each theme gets its own subscription record with its own end_date
    calculated from the purchase date (independent per theme).

    If a theme is already active, purchasing it again EXTENDS the end_date
    by the plan's duration_days from today.

    Body: { "plan_id": <int>, "theme_ids": [<int>, ...] }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BasicThemePurchaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        theme_ids = serializer.validated_data['theme_ids']
        user = request.user
        now = timezone.now()
        end_date = now + timedelta(days=plan.duration_days)

        purchased = []
        for theme_id in theme_ids:
            from program.models import Theme
            theme = Theme.objects.get(id=theme_id)

            # Check for an existing active subscription for this theme
            existing = ThemeSubscription.objects.filter(
                user=user, theme=theme, is_active=True
            ).first()

            if existing:
                # Extend: add duration_days from today
                new_end = now + timedelta(days=plan.duration_days)
                existing.end_date = new_end
                existing.plan = plan
                existing.save(update_fields=['end_date', 'plan'])
                purchased.append(ThemeSubscriptionSerializer(existing).data)
            else:
                # New purchase
                ts = ThemeSubscription.objects.create(
                    user=user,
                    theme=theme,
                    plan=plan,
                    start_date=now,
                    end_date=end_date,
                    is_active=True,
                )
                purchased.append(ThemeSubscriptionSerializer(ts).data)

        return Response({
            'message': f'Successfully purchased {len(purchased)} theme(s) until {end_date:%Y-%m-%d}.',
            'purchased_themes': purchased,
        }, status=status.HTTP_200_OK)


class MyThemeSubscriptionsView(generics.ListAPIView):
    """
    GET: List all of the authenticated user's theme subscriptions (active & expired).
    Add ?active=true to filter only active ones.
    """
    serializer_class = ThemeSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ThemeSubscription.objects.filter(user=self.request.user).select_related('theme', 'plan')
        # Auto-expire stale records
        for ts in qs.filter(is_active=True):
            ts.check_and_update_status()
        if self.request.query_params.get('active') == 'true':
            qs = qs.filter(is_active=True)
        return qs.order_by('-purchased_at')

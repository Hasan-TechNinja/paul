from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Plan, UserSubscription
from .serializers import PlanSerializer, UserSubscriptionSerializer, SubscribeSerializer

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [] # Allow any client to see the plans

class CurrentSubscriptionView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the subscription for the current user, or create a 'free' state if none exists.
        sub, created = UserSubscription.objects.get_or_create(user=self.request.user)
        return sub

class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SubscribeSerializer(data=request.data)
        if serializer.is_valid():
            plan_id = serializer.validated_data['plan_id']
            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)

            # Update the user's subscription record
            user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
            user_sub.plan = plan
            user_sub.is_active = True
            user_sub.start_date = timezone.now()
            # If a strict end_date mapping is needed, it would be calculated here (e.g. +30 days for monthly)
            # For this MVP, we just assign the plan and mark it active.
            user_sub.save()

            return Response({
                "message": f"Successfully subscribed to {plan.name}.",
                "subscription": UserSubscriptionSerializer(user_sub).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

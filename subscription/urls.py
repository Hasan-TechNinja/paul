from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('current/', views.CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
]
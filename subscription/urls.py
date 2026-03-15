from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('plans/', views.PlanListView.as_view(), name='plan-list'),

    # User subscription status (Pro + all theme subscriptions)
    path('current/', views.CurrentSubscriptionView.as_view(), name='current-subscription'),

    # Pro plan purchase (unlocks all themes)
    path('subscribe/pro/', views.ProSubscribeView.as_view(), name='subscribe-pro'),

    # Basic plan — purchase one or more themes (independent per-theme expiry)
    path('subscribe/themes/', views.BasicThemePurchaseView.as_view(), name='subscribe-themes'),

    # List user's per-theme subscriptions (?active=true to filter active only)
    path('my-themes/', views.MyThemeSubscriptionsView.as_view(), name='my-theme-subscriptions'),
]
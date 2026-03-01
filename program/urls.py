from django.urls import path
from .views import ThemeListView, ThemeSessionListView, SessionDetailView, SessionReflectionCreateUpdateView

urlpatterns = [
    path('themes/', ThemeListView.as_view(), name='theme-list'),
    path('themes/<int:theme_id>/sessions/', ThemeSessionListView.as_view(), name='theme-session-list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:session_id>/reflect/', SessionReflectionCreateUpdateView.as_view(), name='session-reflect'),
]

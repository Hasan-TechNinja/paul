from django.urls import path
from . import views

urlpatterns = [
    path('', views.JournalListView.as_view(), name='journal-list'),
    path('<int:pk>/', views.JournalDetailView.as_view(), name='journal-detail'),
    path('<int:pk>/update/', views.JournalDetailView.as_view(), name='journal-update'),
    path('<int:pk>/delete/', views.JournalDetailView.as_view(), name='journal-delete'),
    # path('create/', views.JournalListView.as_view(), name='journal-create'),
]
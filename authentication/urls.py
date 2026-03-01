from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
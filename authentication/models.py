from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class RegisterOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

    def expired(self):
        return self.created_at + timedelta(minutes=3) < timezone.now()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Testimonials(models.Model):
    text = models.TextField()
    issue = models.CharField(max_length=255, blank=True, null=True)
    client_info = models.CharField(max_length=255, default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stars = models.IntegerField(default=0)

    def __str__(self):
        return self.client_info or ""
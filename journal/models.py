from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Journal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    notes = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='journal_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
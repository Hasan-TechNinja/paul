from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Theme(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_free_trial = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='theme_icons/', blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Session(models.Model):
    theme = models.ForeignKey(Theme, related_name='sessions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='session_images/', blank=True, null=True)
    # video_or_audio = models.FileField(upload_to='session_media/', blank=True, null=True)
    text_content = models.TextField(blank=True, help_text="Text to read during the session")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.theme.title} - {self.title}"

class SessionReflection(models.Model):
    user = models.ForeignKey(User, related_name='reflections', on_delete=models.CASCADE)
    session = models.ForeignKey(Session, related_name='reflections', on_delete=models.CASCADE)
    initial_thoughts = models.TextField(blank=True, help_text="What do you see?")
    initial_intensity_level = models.IntegerField(default=1, help_text="1 to 7")
    final_thoughts = models.TextField(blank=True, help_text="What do you feel?")
    final_intensity_level = models.IntegerField(default=1, help_text="1 to 7")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reflection by {self.user.username} on {self.session.title}"

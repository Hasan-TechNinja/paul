from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Theme(models.Model):
    title = models.CharField(max_length=255)
    intro_content = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(blank=True)
    voice_id = models.CharField(max_length=255, blank=True, null=True)
    is_free_trial = models.BooleanField(default=False)
    is_authenticate = models.BooleanField(default=True)
    session_key = models.IntegerField(blank=True, null=True, unique=True)
    icon = models.ImageField(upload_to='theme_icons/', blank=True, null=True)
    icon_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        help_text="Price for a Basic per-theme purchase (reference only; actual billing via plan)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def user_has_access(self, user):
        """
        Returns True if the user is allowed to access this theme's content.
        Access is granted if ANY of the following is true:
          1. The theme is free (is_free_trial=True).
          2. The user has an active Pro subscription (all themes unlocked).
          3. The user has an active Basic per-theme subscription for THIS theme.
        """
        if self.is_free_trial:
            return True
        if not user or not user.is_authenticated:
            return False

        # Check Pro subscription
        from subscription.models import UserSubscription, ThemeSubscription
        try:
            pro_sub = user.subscription  # OneToOne related_name='subscription'
            if pro_sub.is_pro_active:
                return True
        except UserSubscription.DoesNotExist:
            pass

        # Check per-theme Basic subscription
        return ThemeSubscription.objects.filter(
            user=user,
            theme=self,
            is_active=True,
            end_date__gt=timezone.now(),
        ).exists()

class Session(models.Model):
    theme = models.ForeignKey(Theme, related_name='sessions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='session_images/', blank=True, null=True)
    # video_or_audio = models.FileField(upload_to='session_media/', blank=True, null=True)
    text_content = models.JSONField(default=list, blank=True, help_text="Text to read during the session")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.theme.title} - {self.title}"

class SessionReflection(models.Model):
    user = models.ForeignKey(User, related_name='reflections', on_delete=models.CASCADE)
    session = models.ForeignKey(Session, related_name='reflections', on_delete=models.CASCADE)
    see_thoughts = models.TextField(blank=True, help_text="What do you see?")
    see_intensity_level = models.IntegerField(default=1, help_text="1 to 7")
    feel_thoughts = models.TextField(blank=True, help_text="What do you feel?")
    feel_intensity_level = models.IntegerField(default=1, help_text="1 to 7")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reflection by {self.user.username} on {self.session.title}"

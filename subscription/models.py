from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Plan(models.Model):
    INTERVAL_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    PLAN_TYPE_CHOICES = (
        ('pro', 'Pro'),      # Unlocks ALL themes
        ('basic', 'Basic'),  # Per-theme purchase only
    )
    name = models.CharField(max_length=50)  # e.g., Pro, Basic
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES, default='basic')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='monthly')
    features = models.JSONField(default=list, blank=True)  # List of feature strings
    duration_days = models.PositiveIntegerField(
        default=30,
        help_text="Duration in days this plan grants access (e.g. 30 for monthly, 365 for yearly)"
    )

    def __str__(self):
        return f"{self.name} ({self.plan_type}) - ${self.price}/{self.interval}"


class UserSubscription(models.Model):
    """
    Pro plan subscription — grants the user access to ALL themes.
    One record per user; renewed/updated on each Pro purchase.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True, help_text="Leave blank to auto-calculate based on plan duration.")
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan and self.is_active:
            if not self.start_date:
                self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'No Plan'
        return f"{self.user.email} - {plan_name}"

    def check_and_update_status(self):
        """Auto-expire the subscription if end_date has passed."""
        if self.is_active and self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.save(update_fields=['is_active'])
        return self.is_active

    @property
    def is_pro_active(self):
        """Returns True if the user has an active Pro subscription."""
        if not self.plan or self.plan.plan_type != 'pro':
            return False
        return self.check_and_update_status()


class ThemeSubscription(models.Model):
    """
    Basic plan — per-theme purchase.
    Each theme the user purchases gets its own record with independent
    start_date and end_date. Purchasing the same theme again extends its end_date.
    Multiple themes can be purchased in a single transaction (one record per theme).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theme_subscriptions')
    theme = models.ForeignKey(
        'program.Theme', on_delete=models.CASCADE, related_name='subscriptions',
        null=True, blank=True
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True, help_text="Leave blank to auto-calculate based on plan duration.")
    is_active = models.BooleanField(default=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            if not self.start_date:
                self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    class Meta:
        # A user can have multiple records for the same theme (e.g. renewals)
        ordering = ['-purchased_at']


    def __str__(self):
        theme_title = self.theme.title if self.theme else 'Unknown Theme'
        return f"{self.user.email} → {theme_title} (until {self.end_date:%Y-%m-%d})"

    def check_and_update_status(self):
        """Auto-expire this theme subscription if end_date has passed."""
        if self.is_active and timezone.now() > self.end_date:
            self.is_active = False
            self.save(update_fields=['is_active'])
        return self.is_active

    @property
    def days_remaining(self):
        if not self.is_active:
            return 0
        remaining = (self.end_date - timezone.now()).days
        return max(remaining, 0)

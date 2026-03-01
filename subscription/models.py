from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    INTERVAL_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    name = models.CharField(max_length=50) # e.g., Free, Pro, Premium
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='monthly')
    features = models.JSONField(default=list, blank=True) # List of strings

    def __str__(self):
        return f"{self.name} - ${self.price}/{self.interval}"

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'No Plan'
        return f"{self.user.email} - {plan_name}"

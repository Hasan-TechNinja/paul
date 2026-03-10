from django.contrib import admin
from . models import RegisterOTP, Profile

# Register your models here.

class RegisterOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'created_at')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'created_at')

admin.site.register(RegisterOTP, RegisterOTPAdmin)
admin.site.register(Profile, ProfileAdmin)

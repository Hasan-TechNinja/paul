from django.contrib import admin
from . models import RegisterOTP, Profile

# Register your models here.

class RegisterOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'created_at')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'created_at')

admin.site.register(RegisterOTP, RegisterOTPAdmin)
admin.site.register(Profile, ProfileAdmin)



admin.site.site_header = 'I MOVER Admin'
admin.site.site_title = 'I MOVER Admin'
admin.site.index_title = 'Welcome to I MOVER Admin'
from django.contrib import admin
from . models import RegisterOTP, Profile, Testimonials

# Register your models here.

class RegisterOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'created_at')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'created_at')

class TestimonialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'client_info', 'issue', 'created_at')

admin.site.register(RegisterOTP, RegisterOTPAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Testimonials, TestimonialsAdmin)



admin.site.site_header = 'IMOVER Admin'
admin.site.site_title = 'IMOVER Admin'
admin.site.index_title = 'Welcome to IMOVER Admin'
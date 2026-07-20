from rest_framework import serializers
from . models import Testimonials

class TestimonialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonials
        fields = ['id', 'text', 'client_info', 'issue', 'created_at', 'stars']

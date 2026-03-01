from rest_framework import serializers
from .models import Journal

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'user', 'title', 'notes', 'image', 'created_at']
        read_only_fields = ['user', 'created_at']
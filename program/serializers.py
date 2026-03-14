from rest_framework import serializers
from .models import Theme, Session, SessionReflection

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'title', 'description', 'is_free_trial', 'is_authenticate', 'icon', 'icon_url', 'created_at']
    
class SessionReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReflection
        fields = ['id', 'user', 'session', 'initial_thoughts', 'initial_intensity_level', 'final_thoughts', 'final_intensity_level', 'created_at']
        read_only_fields = ['user', 'session']

class SessionSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    reflection = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'theme', 'title', 'subtitle', 'image', 'text_content', 'order', 'is_completed', 'reflection']

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reflections.filter(user=request.user).exists()
        return False

    def get_reflection(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reflection = obj.reflections.filter(user=request.user).first()
            if reflection:
                return SessionReflectionSerializer(reflection).data
        return None

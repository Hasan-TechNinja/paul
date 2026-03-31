from rest_framework import serializers
from .models import Theme, Session, SessionReflection

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'title', 'intro_content', 'description', 'is_free_trial', 'is_authenticate', 'icon', 'icon_url', 'price', 'created_at', 'voice_id', 'session_key']

class SessionReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReflection
        fields = ['id', 'user', 'session', 'see_thoughts', 'see_intensity_level', 'feel_thoughts', 'feel_intensity_level', 'created_at']
        read_only_fields = ['user', 'session']

class SessionSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    reflection = serializers.SerializerMethodField()
    theme_session_key = serializers.CharField(source='theme.session_key', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'theme', 'theme_session_key', 'title', 'subtitle', 'image', 'text_content', 'order', 'is_completed', 'reflection']

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reflections.filter(user=request.user).exists()
        return False

    def get_reflection(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reflections.filter(user=request.user).exists()
        return False

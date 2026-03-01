from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Theme, Session, SessionReflection
from .serializers import ThemeSerializer, SessionSerializer, SessionReflectionSerializer

class ThemeListView(generics.ListAPIView):
    queryset = Theme.objects.all().order_by('created_at')
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticated]

class ThemeSessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        theme_id = self.kwargs.get('theme_id')
        theme = get_object_or_404(Theme, id=theme_id)
        return Session.objects.filter(theme=theme).order_by('order', 'created_at')

class SessionDetailView(generics.RetrieveAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

class SessionReflectionCreateUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        
        reflection, created = SessionReflection.objects.get_or_create(
            user=request.user, 
            session=session,
            defaults={
                'initial_thoughts': request.data.get('initial_thoughts', ''),
                'initial_intensity_level': request.data.get('initial_intensity_level', 1),
                'final_thoughts': request.data.get('final_thoughts', ''),
                'final_intensity_level': request.data.get('final_intensity_level', 1),
            }
        )
        
        if not created:
            reflection.initial_thoughts = request.data.get('initial_thoughts', reflection.initial_thoughts)
            reflection.initial_intensity_level = request.data.get('initial_intensity_level', reflection.initial_intensity_level)
            reflection.final_thoughts = request.data.get('final_thoughts', reflection.final_thoughts)
            reflection.final_intensity_level = request.data.get('final_intensity_level', reflection.final_intensity_level)
            reflection.save()
            
        serializer = SessionReflectionSerializer(reflection)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Theme, Session, SessionReflection
from .serializers import ThemeSerializer, SessionSerializer, SessionReflectionSerializer


class ThemeListView(generics.ListAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Theme.objects.all().order_by('created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user = request.user

        data = []
        for theme in queryset:
            serialized = self.get_serializer(theme).data
            # Annotate each theme with whether the requesting user can access it
            serialized['is_accessible'] = theme.user_has_access(user)
            data.append(serialized)

        return Response(data)


class ThemeSessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        theme_id = self.kwargs.get('theme_id')
        theme = get_object_or_404(Theme, id=theme_id)

        # Check authentication requirement first
        if theme.is_authenticate and not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required to view this theme's sessions.")

        # Check subscription access
        if not theme.user_has_access(self.request.user):
            raise PermissionDenied(
                "You do not have access to this theme. "
                "Purchase a Pro plan to unlock all themes, or purchase this theme individually."
            )

        return Session.objects.filter(theme=theme).order_by('order', 'created_at')


class SessionDetailView(generics.RetrieveAPIView):
    serializer_class = SessionSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        session = get_object_or_404(Session, id=self.kwargs.get('pk'))
        theme = session.theme

        if theme.is_authenticate and not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        if not theme.user_has_access(self.request.user):
            raise PermissionDenied(
                "You do not have access to this theme. "
                "Purchase a Pro plan or this theme individually."
            )

        return session


class SessionReflectionCreateUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)

        reflection, created = SessionReflection.objects.get_or_create(
            user=request.user,
            session=session,
            defaults={
                'see_thoughts': request.data.get('see_thoughts', ''),
                'see_intensity_level': request.data.get('see_intensity_level', 1),
                'feel_thoughts': request.data.get('feel_thoughts', ''),
                'feel_intensity_level': request.data.get('feel_intensity_level', 1),
            }
        )

        if not created:
            reflection.see_thoughts = request.data.get('see_thoughts', reflection.see_thoughts)
            reflection.see_intensity_level = request.data.get('see_intensity_level', reflection.see_intensity_level)
            reflection.feel_thoughts = request.data.get('feel_thoughts', reflection.feel_thoughts)
            reflection.feel_intensity_level = request.data.get('feel_intensity_level', reflection.feel_intensity_level)
            reflection.save()

        serializer = SessionReflectionSerializer(reflection)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

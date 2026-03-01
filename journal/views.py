from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Journal
from .serializers import JournalSerializer
# Create your views here.

class JournalListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Only return journals for the logged-in user
        journals = Journal.objects.filter(user=request.user)
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JournalSerializer(data=request.data)
        if serializer.is_valid():
            # Pass the currently authenticated user to the serializer's save method
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JournalDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Journal.objects.get(pk=pk)
        except Journal.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        journal = self.get_object(pk)
        serializer = JournalSerializer(journal)
        return Response(serializer.data)
    
    def put(self, request, pk):
        journal = self.get_object(pk)
        serializer = JournalSerializer(journal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        journal = self.get_object(pk)
        journal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  
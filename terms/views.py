from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsEducationOfficerOrReadOnly

from .models import Term
from .serializers import TermSerializer


class TermListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        terms = Term.objects.all()
        serializer = TermSerializer(terms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TermSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TermDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Term, pk=pk)

    def get(self, request, pk):
        term = self.get_object(pk)
        return Response(TermSerializer(term).data)

    def put(self, request, pk):
        term = self.get_object(pk)
        serializer = TermSerializer(term, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        term = self.get_object(pk)
        serializer = TermSerializer(term, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        term = self.get_object(pk)
        term.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import School
from education.serializers.school import SchoolSerializer
from users.permissions import IsEducationOfficerOrReadOnly


class SchoolListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        schools = School.objects.all()
        serializer = SchoolSerializer(schools, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SchoolDetailView(APIView):
    permission_classes= [IsEducationOfficerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(School, pk=pk)

    def get(self, request, pk):
        school = self.get_object(pk)
        return Response(SchoolSerializer(school).data)

    def put(self, request, pk):
        school = self.get_object(pk)
        serializer = SchoolSerializer(school, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        school = self.get_object(pk)
        serializer = SchoolSerializer(school, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        school = self.get_object(pk)
        school.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
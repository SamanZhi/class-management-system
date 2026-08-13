from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsEducationOfficerOrReadOnly

from .models import Class, ClassTeacher
from .serializers import (
    ClassDetailSerializer,
    ClassSerializer,
    ClassTeacherSerializer,
)


class ClassListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ClassDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Class, pk=pk)

    def get(self, request, pk):
        class_obj = self.get_object(pk)
        return Response(ClassDetailSerializer(class_obj).data)

    def put(self, request, pk):
        class_obj = self.get_object(pk)
        serializer = ClassSerializer(class_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        class_obj = self.get_object(pk)
        serializer = ClassSerializer(class_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
            class_obj = self.get_object(pk)
            class_obj.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class ClassTeacherListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        assignment = ClassTeacher.objects.all()
        serializer = ClassTeacherSerializer(assignment, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClassTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
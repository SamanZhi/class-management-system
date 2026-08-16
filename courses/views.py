from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsEducationOfficerOrReadOnly

from .models import Course, CourseTeacher
from .serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseTeacherSerializer,
)


class CourseListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        courses = Course.objects.all()
        school_id = request.query_params.get('school')
        term_id = request.query_params.get('term')
        if school_id:
            courses = courses.filter(school_id=school_id)
        if term_id:
            courses = courses.filter(term_id=term_id)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CourseDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Course, pk=pk)

    def get(self, request, pk):
        course_obj = self.get_object(pk)
        return Response(CourseDetailSerializer(course_obj).data)

    def put(self, request, pk):
        course_obj = self.get_object(pk)
        serializer = CourseSerializer(course_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        course_obj = self.get_object(pk)
        serializer = CourseSerializer(course_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
            course_obj = self.get_object(pk)
            course_obj.soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class CourseTeacherListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        assignment = CourseTeacher.objects.all()
        serializer = CourseTeacherSerializer(assignment, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CourseTeacherDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(CourseTeacher, pk=pk)

    def get(self, request, pk):
        assignment = self.get_object(pk)
        return Response(CourseTeacherSerializer(assignment).data)

    def put(self, request, pk):
        assignment = self.get_object(pk)
        serializer = CourseTeacherSerializer(assignment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        assignment = self.get_object(pk)
        serializer = CourseTeacherSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        assignment = self.get_object(pk)
        assignment.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
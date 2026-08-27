from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import Course, CourseTeacher
from education.serializers.course import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseTeacherSerializer,
)
from users.permissions import IsEducationOfficerOrReadOnly


class CourseListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        courses = Course.objects.all()

        school_id = request.query_params.get('school')
        term_id = request.query_params.get('term')
        teacher_id = request.query_params.get('teacher')

        if school_id:
            courses = courses.filter(school_id=school_id)
        if term_id:
            courses = courses.filter(term_id=term_id)
        if teacher_id:
            courses = courses.filter(teacher_assignments__teacher=teacher_id).distinct()

        if request.user.role == 'teacher':
            courses = courses.filter(
                teacher_assignments__teacher=request.user
            ).distinct()

        serializer = CourseSerializer(courses, many=True)

        return Response(serializer.data)


    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, request, pk):
        queryset = Course.objects.all()

        if request.user.role == 'teacher':
            queryset = queryset.filter(
                teacher_assignments__teacher=request.user
            ).distinct()

        return get_object_or_404(queryset, pk=pk)

    def get(self, request, pk):
        course_obj = self.get_object(request, pk)

        return Response(CourseDetailSerializer(course_obj).data)

    def put(self, request, pk):
        course_obj = self.get_object(request, pk)

        serializer = CourseSerializer(course_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, pk):
        course_obj = self.get_object(request, pk)

        serializer = CourseSerializer(course_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
            course_obj = self.get_object(request, pk)

            course_obj.soft_delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


class CourseTeacherListCreateView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get(self, request):
        assignments = CourseTeacher.objects.all()

        if request.user.role == 'teacher':
            assignments = assignments.filter(
                teacher=request.user
            )

        serializer = CourseTeacherSerializer(assignments, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = CourseTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseTeacherDetailView(APIView):
    permission_classes = [IsEducationOfficerOrReadOnly]

    def get_object(self, request, pk):
        queryset = CourseTeacher.objects.all()

        if request.user.role == 'teacher':
            queryset = queryset.filter(teacher=request.user)

        return get_object_or_404(queryset, pk=pk)

    def get(self, request, pk):
        assignment = self.get_object(request, pk)

        return Response(CourseTeacherSerializer(assignment).data)

    def put(self, request, pk):
        assignment = self.get_object(request, pk)

        serializer = CourseTeacherSerializer(assignment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, pk):
        assignment = self.get_object(request, pk)

        serializer = CourseTeacherSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        assignment = self.get_object(request, pk)

        assignment.soft_delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from schools.models import School
from schools.serializers import SchoolSerializer
from terms.models import Term
from terms.serializers import TermSerializer
from users.models import User

from .models import Course, CourseTeacher


class CourseSerializer(serializers.ModelSerializer):
    term = serializers.PrimaryKeyRelatedField(queryset=Term.objects.all())
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all())

    class Meta:
        model = Course
        fields = ['id', 'school', 'term', 'subject', 'duration', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'created_at', 'updated_at']

class CourseTeacherSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TEACHER)
    )

    class Meta:
        model = CourseTeacher
        fields = ['id', 'course_obj', 'teacher', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        course_obj = data.get('course_obj', getattr(self.instance, 'course_obj', None))
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after start date.'}
            )

        qs = CourseTeacher.objects.filter(class_obj=course_obj)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        new_end = end_date or date.max
        for assignment in qs:
            existing_end = assignment.end_date or date.max
            if start_date <= existing_end and assignment.start_date <= new_end:
                raise serializers.ValidationError(
                    'This period overlaps with an existing teacher assignment for this course.'
                )
        return data

class CurrentTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number']

class CourseDetailSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    term = TermSerializer(read_only=True)
    current_teacher = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'school', 'term', 'subject', 'duration', 'current_teacher', 'created_at', 'updated_at']

    def get_current_teacher(self, obj):
        today = timezone.now().date()
        assignment = obj.teacher_assignments.filter(
            start_date__lte=today
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).first()
        if assignment:
            return CurrentTeacherSerializer(assignment.teacher).data
        return None
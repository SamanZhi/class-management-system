from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from education.models import Course, CourseTeacher, School, Term
from users.models import User

from .school import SchoolSerializer
from .term import TermSerializer


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

    def validate(self, attrs):
        course_obj = attrs.get("course_obj", getattr(self.instance, "course_obj", None))
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after start date.'}
            )

        term = course_obj.term

        if start_date < term.start_date:
            raise serializers.ValidationError({"start_date": "تاریخ شروع ارتباط مربی باید داخل بازه ترم باشد."})

        if start_date > term.end_date:
            raise serializers.ValidationError({"start_date": "تاریخ شروع ارتباط مربی باید داخل بازه ترم باشد."})

        if end_date and end_date > term.end_date:
            raise serializers.ValidationError({"end_date": "تاریخ پایان ارتباط مربی باید داخل بازه ترم باشد."})

        qs = CourseTeacher.objects.filter(course_obj=course_obj)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        new_end = end_date or date.max

        for assignment in qs:
            existing_end = assignment.end_date or date.max
            if start_date <= existing_end and assignment.start_date <= new_end:
                raise serializers.ValidationError(
                    'This period overlaps with an existing teacher assignment for this course.'
                )
        return attrs

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
from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import Class, ClassTeacher
from terms.models import Term
from terms.serializers import TermSerializer
from users.models import User

class ClassSerializer(serializers.ModelSerializer):
    term = serializers.PrimaryKeyRelatedField(queryset=Term.objects.all())

    class Meta:
        model = Class
        fields = ['id', 'term', 'subject', 'duration', 'is_deleted', 'created_at', 'updated_at']
        read_only_field = ['id', 'is_deleted', 'created_at', 'updated_at']

class ClassTeacherSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TEACHER)
    )

    class Meta:
        model = ClassTeacher
        fields = ['id', 'class_obj', 'teacher', 'start_date', 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

        def validate(self, data):
            class_obj = data.get('class_obj', getattr(self.instance, 'class_obj', None))
            start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
            end_date = data.get('end_date', getattr(self.instance, 'end_date', None))

            if start_date and end_date and end_date < start_date:
                raise serializers.ValidationError(
                    {'end_date': 'End date must be after start date.'}
                )

            qs = ClassTeacher.objects.filter(class_obj=class_obj)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            new_end = end_date or date.max
            for assignment in qs:
                existing_end = assignment.end_date or date.max
                if start_date <= existing_end and assignment.start_date <= new_end:
                    raise serializers.ValidationError(
                        'This period overlaps with an existing teacher assignment for this class.'
                    )
                return data
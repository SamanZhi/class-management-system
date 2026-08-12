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
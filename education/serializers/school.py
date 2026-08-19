
from rest_framework import serializers

from education.models import School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'address', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'created_at', 'updated_at']
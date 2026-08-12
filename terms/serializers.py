from rest_framework import serializers

from schools.models import School

from .models import Term


class TermSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all())

    class Meta:
        model = Term
        field = ['id', 'school', 'start_date', 'end_date', 'type', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after start date.'}
            )
        return data
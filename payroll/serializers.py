from rest_framework import serializers

from .models import PayrollRecord, TeacherTermRate


class TeacherTermRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTermRate
        fields = (
            'id',
            'teacher',
            'term',
            'base_rate',
        )
        read_only_fields = ('id',)


class PayrollRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRecord
        fields = (
            'id',
            'teacher',
            'year',
            'month',
            'amount',
        )
        read_only_fields = (
            'id',
            'teacher',
            'year',
            'month',
            'amount',
        )
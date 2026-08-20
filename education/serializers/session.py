from rest_framework import serializers

from education.models import Session


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            'id',
            'course_obj',
            'session_number',
            'created_at',
            'updated_at'
        ]

    def validate(self, attrs):
        course = attrs.get('course_obj', getattr(self.instance, 'course_obj', None))
        session_date = attrs.get('date', getattr(self.instance, 'date', None))

        if course and session_date:
            term = course.term

            if not (term.start_date <= session_date <= term.end_date):
                raise serializers.ValidationError({
                    'date': 'Session date must be within the term date range.'
                })

            clash = Session.objects.filter(
                course_obj=course,
                date=session_date
            )

            if self.instance:
                clash = clash.exclude(pk=self.instance.pk)

            if clash.exists():
                raise serializers.ValidationError({
                    'date': 'A session already exists for this course on this date.'
                })

        return attrs
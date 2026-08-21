from django.db import models
from django.utils import timezone
from rest_framework import serializers

from education.models import CourseTeacher, SessionReport


class SessionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReport
        fields = [
            'id',
            'session',
            'summary',
            'present_count',
            'absent_count',
            'status',
            'rejection_reason',
            'teacher',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'teacher',
            'status',
            'rejection_reason',
            'created_at',
            'updated_at'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        teacher = request.user if request else None

        session = attrs.get(
            'session',
            getattr(self.instance, 'session', None)
        )

        if not teacher or not teacher.is_authenticated:
            raise serializers.ValidationError(
                'Authentication is required.'
            )

        if not session:
            raise serializers.ValidationError({
                'session': 'Session is required.'
            })

        if self.instance and 'session' in attrs and attrs['session'] != self.instance.session:
                raise serializers.ValidationError({
                    'session': 'Session cannot be changed after report creation.'
                })

        if session.date > timezone.localdate():
            raise serializers.ValidationError({
                'session': 'You cannot submit a report for a future session.'
            })

        if (self.instance and self.instance.status == SessionReport.Status.APPROVED):
            raise serializers.ValidationError(
                'Approved reports cannot be edited.'
            )

        is_responsible = CourseTeacher.objects.filter(
            course_obj=session.course_obj,
            teacher=teacher,
            start_date__lte=session.date,
        ).filter(
            models.Q(end_date__isnull=True) |
            models.Q(end_date__gte=session.date)
        ).exists()

        if not is_responsible:
            raise serializers.ValidationError({
                'session': (
                    'You were not responsible for this course '
                    'on the session date.'
                )
            })

        return attrs

class SessionReportReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReport
        fields = [
            'status',
            'rejection_reason'
        ]

    def validate(self, attrs):
        status = attrs.get('status')
        rejection_reason = attrs.get('rejection_reason')

        if status == SessionReport.Status.REJECTED and not rejection_reason:
            raise serializers.ValidationError({
                'rejection_reason': (
                    'Rejection reason is required when rejecting a report.'
                )
            })

        if status not in (
            SessionReport.Status.APPROVED,
            SessionReport.Status.REJECTED,
        ):
            raise serializers.ValidationError({
                'status': 'Invalid review status.'
            })

        if self.instance and self.instance.status in (
            SessionReport.Status.APPROVED,
            SessionReport.Status.REJECTED,
        ):
            raise serializers.ValidationError(
                'This report has already been reviewed.'
            )

        return attrs
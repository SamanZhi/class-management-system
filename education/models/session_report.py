from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class SessionReport(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    session = models.OneToOneField('Session', on_delete=models.CASCADE, related_name='reports')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='session_reports')
    summary = models.TextField()
    present_count = models.PositiveIntegerField()
    absent_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_reports')

    def clean(self):
        super().clean()

        if self.teacher and self.teacher.role != 'teacher':
             raise ValidationError({
                  'teacher': 'Only teachers can create session reports.'
             })

        if self.present_count is None:
            raise ValidationError({
                'present_count': 'Present count is required.'
            })

        if self.absent_count is None:
                raise ValidationError({
                    'absent_count': 'Absent count is required.'
                })

        if self.status == self.Status.REJECTED and not self.rejection_reason:
             raise ValidationError({
                  'rejection_reason': 'Rejection reason is required.'
             })
        
    @property
    def is_late(self):
        if not self.updated_at:
            return False

        session_datetime = datetime.combine(
            self.session.date,
            time.min
        )

        session_datetime = timezone.make_aware(
            session_datetime,
            timezone.get_current_timezone
                )

        deadline = session_datetime + timedelta(hours=48)

        return self.updated_at > deadline

    def __str__(self):
        return f"Report for {self.session}"
        



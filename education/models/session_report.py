import math
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
    teacher_edited_at = models.DateTimeField(null=True, blank=True)
    late_reference_at = models.DateTimeField(null=True, blank=True)
    total_late_hours = models.PositiveIntegerField(default=0)

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
        if self.status == self.Status.APPROVED:
            return self.total_late_hours > 0

        if not self.late_reference_at:
            return False

        reference = self.late_reference_at

        if timezone.is_naive(reference):
            reference = timezone.make_aware(
                reference,
                timezone.get_current_timezone(),
            )

        deadline = reference + timedelta(hours=48)

        return timezone.now() > deadline

    def __str__(self):
        return f"Report for {self.session}"

    def get_current_late_hours(self, at=None):
        if not self.late_reference_at:
            return 0

        if at is None:
            at = timezone.now()

        reference = self.late_reference_at

        if timezone.is_naive(reference):
            reference = timezone.make_aware(
                reference,
                timezone.get_current_timezone(),
            )

        if timezone.is_naive(at):
            at = timezone.make_aware(
                at,
                timezone.get_current_timezone(),
            )

        deadline = reference + timedelta(hours=48)

        if at <= deadline:
            return 0

        delay_seconds = (at - deadline).total_seconds()

        return math.ceil(delay_seconds / 3600)

    def mark_teacher_edit(self, edited_at=None):
        if edited_at is None:
            edited_at = timezone.now()

        if timezone.is_naive(edited_at):
            edited_at = timezone.make_aware(
                edited_at,
                timezone.get_current_timezone(),
            )

        current_late_hours = self.get_current_late_hours(
            at=edited_at
        )

        self.total_late_hours += current_late_hours
        self.teacher_edited_at = edited_at

        return current_late_hours

    def initialize_late_cycle(self):
        if self.late_reference_at:
            return

        self.late_reference_at = self.session_datetime

    @property
    def session_datetime(self):
        value = datetime.combine(
            self.session.date,
            time.min,
        )

        return timezone.make_aware(
            value,
            timezone.get_current_timezone(),
        )

    def start_new_late_cycle(self, rejected_at=None):
        if rejected_at is None:
            rejected_at = timezone.now()

        self.late_reference_at = rejected_at
        



from django.conf import settings
from django.db import models

from core.models import BaseModel
from education.models import Term


class TeacherTermRate(BaseModel):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='term_rates'
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name='teacher_rates'
    )
    base_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'term'],
                name='unique_teacher_term_rate',
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.term} - {self.base_rate}"


class PayrollRecord(BaseModel):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    sessions_60 = models.PositiveIntegerField(default=0)
    sessions_90 = models.PositiveIntegerField(default=0)
    sessions_120 = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'year', 'month'],
                name='unique_teacher_payroll_month'
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.year}/{self.month} - {self.amount}"
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, SoftDeleteModel


class Session(BaseModel, SoftDeleteModel):
    course_obj = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='sessions')
    session_number = models.PositiveIntegerField()
    date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['course_obj', 'session_number'],
                name='unique_session_number_per_course'
            )
        ]

    def clean(self):
        super().clean()

        term = self.course_obj.term

        if not (term.start_date <= self.date <= term.end_date):
            raise ValidationError("Session date must be within the term date range.")

        clash = Session.objects.filter(course_obj=self.course_obj, date=self.date).exclude(pk=self.pk)
        
        if clash.exists():
            raise ValidationError("A session already exists for this course on this date.")

    def __str__(self):
        return f"{self.course_obj} - Session {self.session_number}"
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, SoftDeleteModel


class Session(BaseModel, SoftDeleteModel):
    course_obj = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='sessions')
    session_number = models.PositiveIntegerField()
    date = models.DateField()

    class Meta:
        unique_together = ('course_obj', 'session_number')

    def clean(self):
        term = self.course_obj.term
        if not (term.start_date <= self.date <= term.end_data):
            raise ValidationError("تاریخ جلسه باید داخل بازه‌ی ترم باشد.")

        clash = Session.objects.filter(course_obj=self.course_obj, date=self.date).exclude(pk=self.pk)
        if clash.exists():
            raise ValidationError("در این تاریخ قبلاً برای این کلاس جلسه ثبت شده است.")
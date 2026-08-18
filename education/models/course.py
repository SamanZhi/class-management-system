from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseModel, SoftDeleteModel

from .school import School
from .term import Term


class Course(BaseModel, SoftDeleteModel):
    DURATION_CHOICES = (
        (60, '60 minutes'),
        (90, '90 minutes'),
        (120, '120 minutes'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='courses')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='courses')
    subject = models.CharField(max_length=255)
    duration = models.IntegerField(choices=DURATION_CHOICES)

    def __str__(self):
        return f"{self.subject} ({self.duration}min) - {self.term}"


class CourseTeacher(BaseModel, SoftDeleteModel):
    course_obj = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='course_assignments')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def clean(self):
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End_date باید بعد از start_date باشد.")

        term = self.course_obj.term

        if self.start_date < term.start_date or self.start_date > term.end_date:
            raise ValidationError({"start_date": "تاریخ شروع ارتباط مربی باید داخل بازه ترم باشد."})

        if self.end_date and self.end_date > term.end_date:
            raise ValidationError({"end_date": "تاریخ پایان ارتباط مربی باید داخل بازه ترم باشد."})
        
        overlapping = CourseTeacher.objects.filter(
            course_obj=self.course_obj
        ).exclude(pk=self.pk)

        this_end = self.end_date or timezone.max.date()

        for assignment in overlapping:
            other_end = assignment.end_date or timezone.max.date()

            if self.start_date <= other_end and assignment.start_date <= this_end:
                raise ValidationError("این بازه زمانی با مربی دیگری هم پوشانی دارد.")

    def __str__(self):
        return f"{self.teacher} -> {self.course_obj} ({self.start_date} to {self.end_date or 'present'})"
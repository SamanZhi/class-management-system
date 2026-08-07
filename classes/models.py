from django.db import models

from core.models import BaseModel, SoftDeleteModel
from terms.models import Term


class Class(BaseModel, SoftDeleteModel):
    DURATION_CHOICES = (
        (60, '60 minutes'),
        (90, '90 minutes'),
        (120, '120 minutes'),
    )
    
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='classes')
    subject = models.CharField(max_length=255)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.duration}min) - {self.term}"

    class Meta:
        db_table = 'class'
        verbose_name_plural = 'Classes'


class ClassTeacher(BaseModel):
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='class_assignments')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teacher} -> {self.class_obj} ({self.start_date} to {self.end_date or 'present'})"

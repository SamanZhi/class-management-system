from django.db import models

from core.models import BaseModel
from schools.models import School


class Term(BaseModel):
    TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('summer', 'Summer'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='terms')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school.name} - {self.type} ({self.start_date} to {self.end_date})"

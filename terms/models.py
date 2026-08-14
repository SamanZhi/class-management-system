from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, SoftDeleteModel


class Term(BaseModel, SoftDeleteModel):
    TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('summer', 'Summer'),
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End_date باید بعد از start_date باشد.")

    def __str__(self):
        return f"{self.type} - ({self.start_date} to {self.end_date})"
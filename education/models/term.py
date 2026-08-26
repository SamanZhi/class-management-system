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
        if self.start_date.day != 1:
            raise ValidationError({
                'start_date': 'تاریخ شروع ترم باید اول ماه باشد.'
            })

        if self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'تاریخ پایان ترم باید بعد از تاریخ شروع باشد.'})

        overlapping_terms = Term.objects.filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )

        if self.pk:
            overlapping_terms = overlapping_terms.exclude(pk=self.pk)

        if overlapping_terms.exists():
            raise ValidationError({'start_date': 'بازه زمانی این ترم با یک ترم دیگر همپوشانی دارد.'})

    def __str__(self):
        return f'{self.type} - ({self.start_date} to {self.end_date})'
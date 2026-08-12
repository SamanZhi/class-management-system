from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        TEACHER = 'teacher', 'Teacher'
        EDUCATION_OFFICER = 'education_officer', 'Education_Officer'
        FINANCE_OFFICER = 'finance_officer', 'Finance_Officer'

    phone_regex = RegexValidator(
        regex=r'^\+98\d{10}$',
        message="Phone number must be in format '+98XXXXXXXXXX' (10 digits after +98)."
    )

    role = models.CharField(max_length=20, choices=Role.choices)
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True, null=True)
    emergency_number = models.CharField(validators=[phone_regex], max_length=15, blank=True, null=True)

    def clean(self):
        super().clean()
        if self.role == 'teacher':
            errors = {}
            if not self.phone_number:
                errors['phone_number'] = 'Phone number is required for teachers.'
            if not self.emergency_number:
                errors['emergency_number'] = 'Emergency number is required for teachers.'
            if errors:
                raise ValidationError(errors)

    def deactivate(self):
        self.is_active = False
        self.save()
    
    def activate(self):
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.username}"



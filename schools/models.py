from django.db import models

from core.models import BaseModel, SoftDeleteModel


class School(BaseModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name

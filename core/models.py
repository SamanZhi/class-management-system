from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name="حذف شده")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ حذف")
    
    objects = SoftDeleteManager() 
    all_objects = models.Manager() 
    
    class Meta:
        abstract = True  
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

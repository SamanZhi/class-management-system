from django.contrib import admin

from .models import School


@admin.register(School)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    
    list_filter = ('is_deleted',)
    
    search_fields = ('name',)
    
    ordering = ('name',)
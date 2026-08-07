from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'role', 'phone_number', 'emergency_number', 'is_active')
    
    list_filter = ('role', 'is_active')
    
    search_fields = ('username', 'phone_number', 'emergency_number')
    
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Role & Contact', {'fields': ('role', 'phone_number', 'emergency_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'role', 'phone_number', 'emergency_number'),
        }),
    )

from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    message = "فقط مربی‌ها به این بخش دسترسی دارند."

    def has_permission(self, request, view):

        return bool(request.user and request.user.is_authenticated and request.user.role == 'teacher')

class IsEducationOfficer(BasePermission):
    message = "فقط مسئول آموزش به این بخش دسترسی دارد."

    def has_permission(self, request, view):
    
        return bool(request.user and request.user.is_authenticated and request.user.role == 'education_officer')

class IsFinanceOfficer(BasePermission):
    message = "فقط مسئول مالی به این بخش دسترسی دارد."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'finance_officer')

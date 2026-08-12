from rest_framework.permissions import BasePermission, SAFE_METHODS


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

class IsEducationOfficerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'education_officer'
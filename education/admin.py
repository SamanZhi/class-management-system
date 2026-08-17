from django.contrib import admin

from .models import Course, CourseTeacher, School, Term


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_deleted',)
    list_filter = ('is_deleted',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', 'term_type',)
    list_filter = ('term_type',)
    ordering = ('-start_date',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'term', 'subject', 'duration',)
    list_filter = ('school', 'term', 'duration',)
    search_fields = ('subject', 'school__name',)
    ordering = ('-term__start_date',)

@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_object', 'teacher', 'start_date', 'end_date',)
    list_filter = ('teacher', 'start_date', 'end_date',)
    search_fields = ('teacher__username', 'teacher__first_name', 'teacher__last_name', 'course_obj__subject',)
    ordering = ('-start_date',)
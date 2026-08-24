from django.contrib import admin

from .models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'address',
        'is_deleted',
    )

    list_filter = (
        'is_deleted',
    )

    search_fields = (
        'name',
    )

    ordering = (
        'name',
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'start_date',
        'end_date',
        'type',
    )

    list_filter = (
        'type',
    )

    ordering = (
        '-start_date',
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'school',
        'term',
        'subject',
        'duration',
    )

    list_filter = (
        'school',
        'term',
        'duration',
    )

    search_fields = (
        'subject',
        'school__name',
    )

    ordering = (
        '-term__start_date',
    )


@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'course_obj',
        'teacher',
        'start_date',
        'end_date',
    )

    list_filter = (
        'teacher',
        'start_date',
        'end_date',
    )

    search_fields = (
        'teacher__username',
        'teacher__first_name',
        'teacher__last_name',
        'course_obj__subject',
    )

    ordering = (
        '-start_date',
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'course_obj',
        'session_number',
        'date',
        'is_deleted',
    )

    list_filter = (
        'course_obj',
        'date',
        'is_deleted',
    )

    search_fields = (
        'course_obj__subject',
        'course_obj__school__name',
    )

    ordering = (
        '-date',
        'course_obj',
        'session_number',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'course_obj',
                    'session_number',
                    'date',
                ),
            },
        ),
        (
            'System Information',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                    'is_deleted',
                    'deleted_at',
                ),
            },
        ),
    )


@admin.register(SessionReport)
class SessionReportAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'session',
        'teacher',
        'status',
        'present_count',
        'absent_count',
        'is_late',
        'updated_at',
    )

    list_filter = (
        'status',
        'teacher',
        'updated_at',
    )

    search_fields = (
        'session__course_obj__subject',
        'session__course_obj__school__name',
        'teacher__username',
        'teacher__first_name',
        'teacher__last_name',
        'summary',
        'rejection_reason',
    )

    ordering = (
        '-updated_at',
    )

    readonly_fields = (
        'is_late',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        (
            'Report Information',
            {
                'fields': (
                    'session',
                    'teacher',
                    'summary',
                    'present_count',
                    'absent_count',
                ),
            },
        ),
        (
            'Review',
            {
                'fields': (
                    'status',
                    'rejection_reason',
                    'reviewed_by',
                ),
            },
        ),
        (
            'System Information',
            {
                'fields': (
                    'is_late',
                    'created_at',
                    'updated_at',
                ),
            },
        ),
    )
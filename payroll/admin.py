from django.contrib import admin

from .models import PayrollRecord, TeacherTermRate


@admin.register(TeacherTermRate)
class TeacherTermRateAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'term',
        'base_rate',
        'created_at',
    )

    list_filter = (
        'term',
    )

    search_fields = (
        'teacher__username',
    )

    ordering = (
        '-term__start_date',
        'teacher__username',
    )

    list_select_related = (
        'teacher',
        'term',
    )


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = (
        'teacher',
        'year',
        'month',
        'amount',
        'sessions_60',
        'sessions_90',
        'sessions_120',
    )

    list_filter = (
        'year',
        'month',
    )

    search_fields = (
        'teacher__username',
    )

    ordering = (
        '-year',
        '-month',
        'teacher__username',
    )

    list_select_related = (
        'teacher',
    )

    readonly_fields = (
        'teacher',
        'year',
        'month',
        'amount',
        'sessions_60',
        'sessions_90',
        'sessions_120',
    )
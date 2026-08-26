from django.urls import path

from payroll.views.payroll import (
    PayrollCalculateAllView,
    PayrollMonthlyListView,
    TeacherPayrollHistoryView,
)
from payroll.views.teacher_term_rate import TeacherTermRateListCreateView

urlpatterns = [
    path(
        'rates/',
        TeacherTermRateListCreateView.as_view(),
        name='teacher-term-rate-list-create'
    ),
    path(
        'calculate/',
        PayrollCalculateAllView.as_view(),
        name='payroll-calculate-all'
    ),
    path(
        'monthly/',
        PayrollMonthlyListView.as_view(),
        name='payroll-monthly-list'
    ),
    path(
        'my-payroll/',
        TeacherPayrollHistoryView.as_view(),
        name='teacher-payroll-history'
    ),
]

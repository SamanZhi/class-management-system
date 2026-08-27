from django.urls import path

from education.views.course import (
    CourseDetailView,
    CourseListCreateView,
    CourseTeacherDetailView,
    CourseTeacherListCreateView,
)
from education.views.school import SchoolDetailView, SchoolListCreateView
from education.views.session import SessionDetailView, SessionListCreateView
from education.views.session_report import (
    SessionReportDetailView,
    SessionReportListCreateView,
    SessionReportReviewView,
    TeacherMonthlyReportSummaryView,
)
from education.views.term import TermDetailView, TermListCreateView

urlpatterns = [
    path('schools/', SchoolListCreateView.as_view(), name='school-list'),
    path('schools/<int:pk>/', SchoolDetailView.as_view(), name='school-detail'),
    path('terms/', TermListCreateView.as_view(), name='term-list'),
    path('terms/<int:pk>/', TermDetailView.as_view(), name='term-detail'),
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/teachers/', CourseTeacherListCreateView.as_view(), name='course-teacher-list'),
    path('courses/teachers/<int:pk>/', CourseTeacherDetailView.as_view(), name='course-teacher-detail'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('sessions/', SessionListCreateView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
    path('session-reports/', SessionReportListCreateView.as_view(), name='session-report-list'),
    path('session-reports/monthly-summary/', TeacherMonthlyReportSummaryView.as_view(), name='teacher-monthly-report-summary'),
    path('session-reports/<int:pk>/', SessionReportDetailView.as_view(), name='session-report-detail'),
    path('session-reports/<int:pk>/review/', SessionReportReviewView.as_view(), name='session-report-review')
]

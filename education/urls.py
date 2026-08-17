from django.urls import path

from education.views.course import (
    CourseDetailView,
    CourseListCreateView,
    CourseTeacherDetailView,
    CourseTeacherListCreateView,
)
from education.views.school import SchoolDetailView, SchoolListCreateView
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
]

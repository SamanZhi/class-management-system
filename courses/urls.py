from django.urls import path

from .views import (
    CourseDetailView,
    CourseListCreateView,
    CourseTeacherDetailView,
    CourseTeacherListCreateView,
)

app_name = 'classes'

urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list-create'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('teachers/', CourseTeacherListCreateView.as_view(), name='course-teacher-list-create'),
    path('teachers/<int:pk>/', CourseTeacherDetailView.as_view(), name='course-teacher-detail')
]
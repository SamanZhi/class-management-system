from django.urls import path

from .views import (
    ClassDetailView,
    ClassListCreateView,
    ClassTeacherDetailView,
    ClassTeacherListCreateView,
)

app_name = 'terms'

urlpatterns = [
    path('', ClassListCreateView.as_view(), name='class-list-create'),
    path('<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('<teachers/', ClassTeacherListCreateView.as_view(), name='class-teacher-list-create'),
    path('teachers/<int:pk>/', ClassTeacherDetailView.as_view(), name='class-teacher-detail')
]
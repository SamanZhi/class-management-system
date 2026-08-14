from django.urls import path

from .views import SchoolDetailView, SchoolListCreateView

app_name = 'schools'

urlpatterns = [
    path('', SchoolListCreateView.as_view(), name='school-list-create'),
    path('<int:pk>/', SchoolDetailView.as_view(), name='school-detail'),
]
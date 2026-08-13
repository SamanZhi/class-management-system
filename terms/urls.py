from django.urls import path

from .views import TermDetailView, TermListCreateView

app_name = 'terms'

urlpatterns = [
    path('', TermListCreateView.as_view(), name='term-list-create'),
    path('<int:pk>/', TermDetailView.as_view(), name='term-detail')
]
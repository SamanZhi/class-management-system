from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    EducationOfficerDashboardView,
    FinanceOfficerDashboardView,
    MeView,
    ProfileView,
    TeacherDashboardView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_obtain_refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('dashboard/teacher/', TeacherDashboardView.as_view, name='teacher-dashboard'),
    path('dashboard/education-officer/', EducationOfficerDashboardView.as_view, name='education-officer-dashboard'),
    path('dashboard/finance-officer/', FinanceOfficerDashboardView.as_view, name='finance-officer-dashboard'),
]

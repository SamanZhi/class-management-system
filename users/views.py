from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserProfileSerializer

from .permissions import IsEducationOfficer, IsFinanceOfficer, IsTeacher


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "phone_number": user.phone_number,
            "emergency_number": user.emergency_number
        })

class ProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

class TeacherDashboardView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({"message": "مربی گرامی خوش آمدید"})

class EducationOfficerDashboardView(APIView):
    permission_classes = [IsEducationOfficer]

    def get(self, request):
        return Response({"message": "مسئول آموزش گرامی خوش آمدید"})

class FinanceOfficerDashboardView(APIView):
    permission_classes = [IsFinanceOfficer]

    def get(self, request):
        return Response({"message": "مسئول مالی گرامی خوش آمدید"})


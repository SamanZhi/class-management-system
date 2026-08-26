from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import TeacherTermRate
from payroll.serializers import TeacherTermRateSerializer
from users.models import User
from users.permissions import IsFinanceOfficer


class TeacherTermRateListCreateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFinanceOfficer,
    ]

    def post(self, request):
        serializer = TeacherTermRateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        teacher_id = serializer.validated_data['teacher'].id

        teacher = User.objects.filter(
            id=teacher_id,
            role=User.Role.TEACHER,
            is_active=True,
        ).first()

        if teacher is None:
            return Response(
                {
                    'detail': (
                        'Teacher does not exist or is inactive.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        rate = serializer.save()

        return Response(
            TeacherTermRateSerializer(rate).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        rates = TeacherTermRate.objects.select_related(
            'teacher',
            'term',
        ).order_by(
            'term__start_date',
            'teacher__username',
        )

        serializer = TeacherTermRateSerializer(
            rates,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
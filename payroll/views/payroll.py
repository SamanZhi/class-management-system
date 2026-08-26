from django.utils.dateparse import parse_date

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import PayrollRecord
from payroll.serializers import PayrollRecordSerializer
from payroll.services import calculate_teacher_payroll
from users.models import User
from users.permissions import IsFinanceOfficer, IsTeacher


def get_year_month(request):
    year = request.query_params.get('year')
    month = request.query_params.get('month')

    if not year or not month:
        return None, None, Response(
            {
                'detail': 'year and month are required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return None, None, Response(
            {
                'detail': 'year and month mus be integers.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if not 1 <= month <= 12:
        return None, None, Response(
            {
                'detail': 'month must be between 1 and 12.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PayrollCalculateAllView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFinanceOfficer,
    ]

    def post(self, request):
        year, month, error_response = get_year_month(
            request
        )

        if error_response:
            return error_response

        teachers = User.objects.filter(
            role=User.Role.TEACHER,
            is_active=True,
        )

        payrolls = []

        for teacher in teachers:
            payroll = calculate_teacher_payroll(
                teacher=teacher,
                year=year,
                month=month,
            )

            if payroll is not None:
                payrolls.append(payroll)

        serializer = PayrollRecordSerializer(
            payrolls,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PayrollMonthlyListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsFinanceOfficer,
    ]

    def get(self, request):
        year, month, error_response = get_year_month(
            request
        )

        if error_response:
            return error_response

        payrolls = PayrollRecord.objects.filter(
            year=year,
            month=month,
        ). select_related(
            'teacher',
        ).order_by(
            'teacher__username',
        )

        serializer = PayrollRecordSerializer(
            payrolls,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    

from django.db.models import Count, Q
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import SessionReport
from education.serializers.session_report import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
    TeacherMonthlyReportSummarySerializer,
)


class SessionReportListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        reports = SessionReport.objects.select_related(
            'session',
            'session__course_obj',
            'session__course_obj__school',
            'session__course_obj__term',
            'teacher',
            'reviewed_by',
        )

        if request.user.role == 'teacher':
            reports = reports.filter(teacher=request.user)

        elif request.user.role == 'education_officer':
            pass

        else:
            return None

        school_id = request.query_params.get('school')
        course_id = request.query_params.get('course')
        teacher_id = request.query_params.get('teacher')

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if school_id:
            reports = reports.filter(
                session__course_obj__school_id=school_id
            )

        if course_id:
            reports = reports.filter(
                session__course_obj_id=course_id
            )

        if teacher_id:
            reports = reports.filter(
                teacher_id=teacher_id
            )

        if start_date:
            parsed_start_date = parse_date(start_date)

            if parsed_start_date:
                reports = reports.filter(
                    session__date__gte=parsed_start_date
                )

        if end_date:
            parsed_end_date = parse_date(end_date)

            if parsed_end_date:
                reports = reports.filter(
                    session__date__lte=parsed_end_date
                )

        return reports.order_by('-session__date', '-id')

    def get(self, request):
        if request.user.role not in [
            'teacher',
            'education_officer',
        ]:
            return Response(
                {
                    'detail': (
                        'Only teachers and education officers '
                        'can access session reports.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        reports = self.get_queryset(request)

        serializer = SessionReportSerializer(
            reports,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.user.role != 'teacher':
            return Response(
                {
                    'detail': 'Only teachers can create session reports.'
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SessionReportSerializer(
            data=request.data,
            context={'request': request},
        )

        if serializer.is_valid():
            report = serializer.save(
                teacher=request.user,
            )

            report.mark_teacher_edit()
            report.late_reference_at = report.teacher_edited_at
            report.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class SessionReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SessionReport.objects.select_related(
                'session',
                'session__course_obj',
                'session__course_obj__school',
                'session__course_obj__term',
                'teacher',
                'reviewed_by',
            ).get(pk=pk)

        except SessionReport.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role not in [
            'teacher',
            'education_officer',
        ]:
            return Response(
                {
                    'detail': (
                        'Only teachers and education officers '
                        'can access session reports.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        report = self.get_object(pk)

        if report is None:
            return Response(
                {'detail': 'Session report not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            request.user.role == 'teacher'
            and report.teacher_id != request.user.id
        ):
            return Response(
                {'detail': 'You cannot access this report.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SessionReportSerializer(report)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk, *args, **kwargs):
        try:
            report = self.get_object(pk)
        except SessionReport.DoesNotExist:
            return Response(
                {"detail": "Report not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.teacher != request.user:
            return Response(
                {"detail": "You are not allowed to edit this report."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if report.status == SessionReport.Status.APPROVED:
            return Response(
                {"detail": "Approved reports cannot be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        was_rejected = report.status == SessionReport.Status.REJECTED

        serializer = SessionReportSerializer(
            report,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        report = serializer.save()

        if was_rejected:
            report.status = SessionReport.Status.PENDING
            report.rejection_reason = ''
            report.reviewed_by = None
            report.mark_teacher_edit()
            report.late_reference_at = report.teacher_edited_at
            report.save(update_fields=[
                'status',
                'rejection_reason',
                'reviewed_by',
                'teacher_edited_at',
                'total_late_hours',
                'late_reference_at',
            ])

        return Response(
            SessionReportSerializer(report, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class TeacherMonthlyReportSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'teacher':
            return Response(
                {
                    'detail': (
                        'Only teachers can access monthly report summary.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))
        except (TypeError, ValueError):
            return Response(
                {
                    'detail': 'Year and month are required and must be integers.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if month < 1 or month > 12:
            return Response(
                {'detail': 'Month must be between 1 and 12.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reports = SessionReport.objects.filter(
            teacher=request.user,
            session__date__year=year,
            session__date__month=month,
        )

        summary = reports.aggregate(
            approved=Count(
                'id',
                filter=Q(status=SessionReport.Status.APPROVED),
            ),
            rejected=Count(
                'id',
                filter=Q(status=SessionReport.Status.REJECTED),
            ),
            pending=Count(
                'id',
                filter=Q(status=SessionReport.Status.PENDING),
            ),
        )

        data = {
            'year': year,
            'month': month,
            'approved': summary['approved'],
            'rejected': summary['rejected'],
            'pending': summary['pending'],
        }

        serializer = TeacherMonthlyReportSummarySerializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

class SessionReportReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SessionReport.objects.select_related(
                'session',
                'session__course_obj',
                'teacher',
                'reviewed_by',
            ).get(pk=pk)

        except SessionReport.DoesNotExist:
            return None

    def patch(self, request, pk):
        if request.user.role != 'education_officer':
            return Response(
                {
                    'detail': (
                        'Only education officers '
                        'can review reports.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        report = self.get_object(pk)

        if report is None:
            return Response(
                {'detail': 'Session report not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.status == SessionReport.Status.APPROVED:
            return Response(
                {
                    'detail': (
                        'Approved reports cannot be reviewed again.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SessionReportReviewSerializer(
            report,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save(
                reviewed_by=request.user
            )

            if report.status == SessionReport.Status.REJECTED:
                report.start_new_late_cycle()
                report.save(
                    update_fields=[
                        'late_reference_at',
                        'updated_at',
                    ]
                )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
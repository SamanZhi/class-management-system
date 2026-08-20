from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import SessionReport
from education.serializers.session_report import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
)


class SessionReportListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'teacher':
            return Response(
                {'detail': 'Only teachers can access sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        reports = SessionReport.objects.filter(
            teacher=request.user
        ).select_related(
            'session',
            'session__course_obj',
            'session__course_obj__school',
            'session__course_obj__term'
        )

        serializer = SessionReportSerializer(
            reports,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'teacher':
            return Response(
                {'detail': 'Only teachers can access sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SessionReportSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(
                teacher=request.user
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SessionReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SessionReport.objects.select_related(
                'session',
                'session__course_obj',
                'session__course_obj__school',
                'session_course_obj__term',
                'teacher',
                'reviewed_by'
        ).get(pk=pk)
        except SessionReport.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role != 'teacher':
            return Response(
                {'detail': 'Only teachers can access sessions reports.'},
                status=status.HTTP_403_FORBIDDEN
            )

        report = self.get_object(pk)

        if report is None:
            return Response(
                {'detail': 'Session report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if report.teacher != request.user:
            return Response(
                {'detail': 'You cannot access this report.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SessionReportSerializer(report)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role != 'teacher':
                return Response(
                    {'detail': 'Only teachers can update sessions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        report = self.get_object(pk)

        if report is None:
            return Response(
                {'detail': 'Session report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if report.teacher != request.user:
            return Response(
                {'detail': 'You cannot edit this report.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SessionReportSerializer(
            report, 
            data=request.data, 
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(
                teacher=request.user
            )

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SessionReportReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SessionReport.objects.select_related(
                'session',
                'session__course_obj',
                'teacher',
                'reviewed_by'
        ).get(pk=pk)
        except SessionReport.DoesNotExist:
            return None

    def patch(self, request, pk):
        if request.user.role != 'education_officer':
                return Response(
                    {'detail': 'Only education officers can review reports.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        report = self.get_object(pk)
        
        if report is None:
            return Response(
                {'detail': 'Session report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SessionReportReviewSerializer(
            report,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save(
                reviewed_by=request.user
            )

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
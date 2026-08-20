from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import SessionReport
from education.serializers.session_report import SessionReportSerializer


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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import Session
from education.serializers.session import SessionSerializer


class SessionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'education_officer':
            return Response(
                {'detail': 'Only education officers can access sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        sessions = Session.objects.select_related(
            'course_obj',
            'course_obj__school',
            'course_obj__term'
        )

        serializer = SessionSerializer(sessions, many=True)

        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'education_officer':
            return Response(
                {'detail': 'Only education officers can create sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SessionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return self.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
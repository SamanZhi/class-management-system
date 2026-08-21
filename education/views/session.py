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
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Session.objects.select_related(
                'course_obj',
                'course_obj__school',
                'course_obj__term'
        ).get(pk=pk)
        except Session.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role != 'education_officer':
            return Response(
                {'detail': 'Only education officers can access sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        session = self.get_object(pk)

        if session is None:
            return Response(
                {'detail': 'Session not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SessionSerializer(session)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role != 'education_officer':
                return Response(
                    {'detail': 'Only education officers can update sessions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
       
        session = self.get_object(pk)

        if session is None:
            return Response(
                {'detail': 'Session not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SessionSerializer(session, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if request.user.role != 'education_officer':
            return Response(
                {'detail': 'Only education officers can delete sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )
               
        session = self.get_object(pk)

        if session is None:
            return Response(
                {'detail': 'Session not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        session.soft_delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
from datetime import date

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from education.serializers.session_report import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
)
from users.models import User


class SessionReportSerializerTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name='School A',
            address='Address A',
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
            type='regular',
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )

        self.other_teacher = User.objects.create_user(
            username='new_teacher',
            password='pass321',
            role='teacher',
            phone_number='+989123456788',
            emergency_number='+989876543211',
        )

        self.education_officer = User.objects.create_user(
            username='education_officer',
            password='pass456',
            role='education_officer',
            phone_number='+989123456787',
            emergency_number='+989876543212',
        )

        self.session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

    def get_context(self, user):
        request = self.factory.post('/session-reports/')
        request.user = user

        return {'request': request}

    def valid_data(self):
        return {
            'session': self.session.id,
            'summary': 'Students completed the lesson.',
            'present_count': 15,
            'absent_count': 2,
        }

    def test_valid_report_data(self):
        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_future_session_is_invalid(self):
        future_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2099, 1, 1),
        )

        data = self.valid_data()
        data['session'] = future_session.id

        serializer = SessionReportSerializer(
            data=data,
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)
from datetime import date

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from users.models import User


class SessionReportViewTests(APITestCase):

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
            username='test_education_officer',
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

        self.list_url = '/session-reports/'

    def create_report(self):
        return SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Original summary',
            present_count=15,
            absent_count=2,
        )

    def test_teacher_can_create_report(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': self.session.id,
                'summary': 'Today we covered Python.',
                'present_count': 15,
                'absent_count': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            session=self.session
        )

        self.assertEqual(
            report.teacher,
            self.teacher,
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_teacher_can_only_see_own_reports(self):
        own_report = self.create_report()

        other_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        SessionReport.objects.create(
            session=other_session,
            teacher=self.other_teacher,
            summary='Other teacher report',
            present_count=10,
            absent_count=5,
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]['id'],
            own_report.id,
        )

    def test_teacher_cannot_edit_another_teachers_report(self):
        other_report = SessionReport.objects.create(
            session=self.session,
            teacher=self.other_teacher,
            summary='Other report',
            present_count=10,
            absent_count=5,
        )

        url = f'/session-reports/{other_report.id}/'

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.put(
            url,
            {
                'summary': 'Hacked report',
                'present_count': 100,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_cannot_submit_future_session_report(self):
        future_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2099, 1, 1),
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': future_session.id,
                'summary': 'Future report',
                'present_count': 10,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unassigned_teacher_cannot_submit_report(self):
        self.client.force_authenticate(
            user=self.other_teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': self.session.id,
                'summary': 'Unauthorized report',
                'present_count': 10,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
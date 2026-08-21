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
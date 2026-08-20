from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from django.test import TestCase

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from users.models import User


class SessionReportModelTests(TestCase):
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
            username='test-teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
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

    def create_report(self):
        return SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Test session report',
            present_count=15,
            absent_count=2,
        )

    def test_create_session_report(self):
        report = self.create_report()

        self.assertEqual(report.session, self.session)
        self.assertEqual(report.teacher, self.teacher)
        self.assertEqual(report.present_count, 15)
        self.assertEqual(report.absent_count, 2)
        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_one_report_per_session(self):
        self.create_report()

        with self.assertRaises(Exception):
            SessionReport.objects.create(
                session=self.session,
                teacher=self.teacher,
                summary='Test session report 2',
                present_count=10,
                absent_count=5,
            )
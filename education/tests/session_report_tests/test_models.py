from datetime import date, datetime
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

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

        with self.assertRaises(IntegrityError):
            SessionReport.objects.create(
                session=self.session,
                teacher=self.teacher,
                summary='Test session report 2',
                present_count=10,
                absent_count=5,
            )

    def test_is_late_is_false_before_48_hours(self):
        report = self.create_report()

        updated_at = timezone.make_aware(2026, 9, 6, 12, 0)

        with patch.object(
            SessionReport,
            'updated_at',
            updated_at,
        ):
            self.assertFalse(report.is_late)

    def test_is_late_is_false_at_exactly_48_hours(self):
        report = self.create_report()

        updated_at = datetime.fromisoformat(
            '2026-09-06T12:00:00+00:00'
        )

        with patch.object(
            SessionReport,
            'updated_at',
            updated_at,
        ):
            self.assertFalse(report.is_late)

    def test_is_late_is_true_after_48_hours(self):
        report = self.create_report()

        updated_at = datetime.fromisoformat(
            '2026-09-07T00:00:00+00:00'
        )

        with patch.object(
            SessionReport,
            'updated_at',
            updated_at,
        ):
            self.assertTrue(report.is_late)

    def test_is_late_is_recalculated_after_report_update(self):
        report = self.create_report()

        first_updated_at = datetime.fromisoformat(
            '2026-09-07T00:01:00+00:00'
        )

        with patch.object(
            SessionReport,
            'updated_at',
            first_updated_at,
        ):
            self.assertFalse(report.is_late)

        second_updated_at = datetime.fromisoformat(
            '2026-09-07T00:01:00+00:00'
        )

        with patch.object(
            SessionReport,
            'updated_at',
            second_updated_at,
        ):
            self.assertTrue(report.is_late)

    def test_rejection_reason_can_be_stored(self):
        report = self.create_report()

        report.status = SessionReport.Status.REJECTED
        report.rejection_reason = 'Please correct attendance.'
        report.save()

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.REJECTED,
        )
        self.assertEqual(
            report.rejection_reason,
            'Please correct attendance.',
        )
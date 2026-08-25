from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from education.models import Course, CourseTeacher, School, Session, SessionReport, Term
from users.models import User


class SessionReportModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='School A', address='Address A')
        self.term = Term.objects.create(
            start_date=date(2026, 8, 1),
            end_date=date(2026, 10, 31),
            type='regular',
        )
        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )
        self.teacher = User.objects.create_user(
            username='test_teacher', password='pass123', role='teacher',
            phone_number='+989123456789', emergency_number='+989876543210',
        )
        self.session = Session.objects.create(
            course_obj=self.course, session_number=1, date=date(2026, 8, 5),
        )
        CourseTeacher.objects.create(
            course_obj=self.course, teacher=self.teacher,
            start_date=date(2026, 8, 1), end_date=date(2026, 10, 31),
        )

    def create_report(self, **kwargs):
        data = {
            'session': self.session, 'teacher': self.teacher,
            'summary': 'Test session report', 'present_count': 15, 'absent_count': 2,
        }
        data.update(kwargs)
        return SessionReport.objects.create(**data)

    def aware(self, value):
        return timezone.make_aware(datetime.fromisoformat(value), timezone.get_current_timezone())

    def test_create_session_report(self):
        report = self.create_report()
        self.assertEqual(report.status, SessionReport.Status.PENDING)
        self.assertEqual(report.total_late_hours, 0)
        self.assertIsNone(report.late_reference_at)

    def test_one_report_per_session(self):
        self.create_report()
        with self.assertRaises(IntegrityError):
            self.create_report()

    def test_initialize_late_cycle_uses_session_datetime(self):
        report = self.create_report()
        report.initialize_late_cycle()
        self.assertEqual(report.late_reference_at, report.session_datetime)

    def test_initialize_late_cycle_does_not_overwrite_existing_reference(self):
        report = self.create_report()
        reference = self.aware('2026-08-06T10:00:00')
        report.late_reference_at = reference
        report.initialize_late_cycle()
        self.assertEqual(report.late_reference_at, reference)

    def test_current_late_hours_is_zero_before_48_hours(self):
        report = self.create_report()
        report.initialize_late_cycle()
        at = self.aware('2026-08-06T12:00:00')
        self.assertEqual(report.get_current_late_hours(at), 0)

    def test_current_late_hours_is_zero_at_exactly_48_hours(self):
        report = self.create_report()
        report.initialize_late_cycle()
        at = self.aware('2026-08-07T00:00:00')
        self.assertEqual(report.get_current_late_hours(at), 0)

    def test_current_late_hours_is_one_after_one_hour(self):
        report = self.create_report()
        report.initialize_late_cycle()
        at = self.aware('2026-08-07T01:00:00')
        self.assertEqual(report.get_current_late_hours(at), 1)

    def test_current_late_hours_rounds_one_hour_and_twenty_minutes_up(self):
        report = self.create_report()
        report.initialize_late_cycle()
        at = self.aware('2026-08-07T01:20:00')
        self.assertEqual(report.get_current_late_hours(at), 2)

    def test_pending_report_becomes_late_after_48_hours(self):
        report = self.create_report()
        report.initialize_late_cycle()

        with patch('education.models.session_report.timezone.now') as mock_now:
            mock_now.return_value = report.late_reference_at + timedelta(hours=49)

            self.assertTrue(report.is_late)

    def test_pending_report_is_not_late_at_48_hours(self):
        report = self.create_report()
        report.initialize_late_cycle()

        with patch('education.models.session_report.timezone.now') as mock_now:
            mock_now.return_value = report.late_reference_at + timedelta(hours=48)

            self.assertFalse(report.is_late)

    def test_approved_report_is_late_only_when_total_late_hours_is_positive(self):
        report = self.create_report(status=SessionReport.Status.APPROVED)
        self.assertFalse(report.is_late)
        report.total_late_hours = 1
        self.assertTrue(report.is_late)

    def test_mark_teacher_edit_adds_current_cycle_late_hours(self):
        report = self.create_report()
        report.initialize_late_cycle()
        edited_at = self.aware('2026-08-07T01:20:00')
        current = report.mark_teacher_edit(edited_at)
        self.assertEqual(current, 2)
        self.assertEqual(report.total_late_hours, 2)
        self.assertEqual(report.teacher_edited_at, edited_at)

    def test_late_hours_are_accumulated_across_multiple_cycles(self):
        report = self.create_report()
        report.initialize_late_cycle()
        report.mark_teacher_edit(self.aware('2026-08-07T01:00:00'))
        report.start_new_late_cycle(self.aware('2026-08-07T10:00:00'))
        report.mark_teacher_edit(self.aware('2026-08-09T11:20:00'))
        self.assertEqual(report.total_late_hours, 3)

    def test_start_new_late_cycle_sets_rejection_time(self):
        report = self.create_report()
        rejected_at = self.aware('2026-08-07T10:00:00')
        report.start_new_late_cycle(rejected_at)
        self.assertEqual(report.late_reference_at, rejected_at)

    def test_rejection_reason_is_required(self):
        report = self.create_report(status=SessionReport.Status.REJECTED)
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_rejection_reason_can_be_stored(self):
        report = self.create_report(
            status=SessionReport.Status.REJECTED,
            rejection_reason='Please correct attendance.',
        )
        report.full_clean()
        self.assertEqual(report.rejection_reason, 'Please correct attendance.')

    def test_only_teacher_can_be_report_teacher(self):
        officer = User.objects.create_user(
            username='officer', password='pass123', role='education_officer',
            phone_number='+989123456700', emergency_number='+989123456701',
        )
        report = SessionReport(
            session=self.session, teacher=officer,
            summary='Invalid', present_count=10, absent_count=5,
        )
        with self.assertRaises(ValidationError):
            report.full_clean()

from datetime import date
from decimal import Decimal

from django.test import TestCase

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from payroll.models import PayrollRecord, TeacherTermRate
from payroll.services import (
    calculate_teacher_payroll,
    get_late_penalty,
    get_session_base_wage,
)
from users.models import User


class PayrollServiceTests(TestCase):

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

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )

        self.rate = TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        self.course_90 = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )

        self.course_60 = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Django',
            duration=60,
        )

        self.course_120 = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='DRF',
            duration=120,
        )

        CourseTeacher.objects.create(
            course_obj=self.course_90,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

        CourseTeacher.objects.create(
            course_obj=self.course_60,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

        CourseTeacher.objects.create(
            course_obj=self.course_120,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

    def create_session(
        self,
        course,
        session_number,
        session_date,
    ):
        return Session.objects.create(
            course_obj=course,
            session_number=session_number,
            date=session_date,
        )

    def create_report(
        self,
        session,
        status=SessionReport.Status.APPROVED,
        total_late_hours=0,
    ):
        return SessionReport.objects.create(
            session=session,
            teacher=self.teacher,
            summary='Test session report',
            present_count=10,
            absent_count=2,
            status=status,
            total_late_hours=total_late_hours,
        )

    def test_60_minute_session_has_70_percent_of_base_rate(self):
        session = self.create_session(
            self.course_60,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(session)

        wage = get_session_base_wage(
            report,
            Decimal(10),
        )

        self.assertEqual(wage, Decimal(7))

    def test_90_minute_session_has_full_base_rate(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(session)

        wage = get_session_base_wage(
            report,
            Decimal(10),
        )

        self.assertEqual(wage, Decimal(10))

    def test_120_minute_session_has_130_percent_of_base_rate(self):
        session = self.create_session(
            self.course_120,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(session)

        wage = get_session_base_wage(
            report,
            Decimal(10),
        )

        self.assertEqual(wage, Decimal(13))

    def test_report_without_late_hours_has_no_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(
            session,
            total_late_hours=0,
        )

        self.assertEqual(
            get_late_penalty(report),
            Decimal(0),
        )

    def test_one_late_hour_has_one_percent_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(
            session,
            total_late_hours=1,
        )

        self.assertEqual(
            get_late_penalty(report),
            Decimal('0.01'),
        )

    def test_two_late_hours_have_two_percent_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(
            session,
            total_late_hours=2,
        )

        self.assertEqual(
            get_late_penalty(report),
            Decimal('0.02'),
        )

    def test_late_penalty_is_capped_at_100_percent(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(
            session,
            total_late_hours=150,
        )

        self.assertEqual(
            get_late_penalty(report),
            Decimal('1.0'),
        )

    def test_calculates_basic_wage_for_60_90_and_120_sessions(self):
        session_90 = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        session_60 = self.create_session(
            self.course_60,
            1,
            date(2026, 9, 6),
        )

        session_120 = self.create_session(
            self.course_120,
            1,
            date(2026, 9, 7),
        )

        self.create_report(session_90)
        self.create_report(session_60)
        self.create_report(session_120)

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            payroll.amount,
            Decimal(30),
        )

        self.assertEqual(payroll.sessions_90, 1)
        self.assertEqual(payroll.sessions_60, 1)
        self.assertEqual(payroll.sessions_120, 1)

    def test_uses_only_approved_reports(self):
        approved_session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        pending_session = self.create_session(
            self.course_90,
            2,
            date(2026, 9, 6),
        )

        rejected_session = self.create_session(
            self.course_90,
            3,
            date(2026, 9, 7),
        )

        self.create_report(
            approved_session,
            SessionReport.Status.APPROVED,
        )

        self.create_report(
            pending_session,
            SessionReport.Status.PENDING,
        )

        self.create_report(
            rejected_session,
            SessionReport.Status.REJECTED,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            payroll.amount,
            Decimal(10),
        )

        self.assertEqual(payroll.sessions_90, 1)

    def test_calculates_payroll_based_on_session_month(self):
        september_session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        october_session = self.create_session(
            self.course_90,
            2,
            date(2026, 10, 5),
        )

        self.create_report(september_session)
        self.create_report(october_session)

        september_payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        october_payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            10,
        )

        self.assertEqual(
            september_payroll.amount,
            Decimal(10),
        )

        self.assertEqual(
            october_payroll.amount,
            Decimal(10),
        )

    def test_late_approved_report_is_included_with_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        report = self.create_report(
            session,
            total_late_hours=1,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        report.refresh_from_db()

        self.assertTrue(report.is_late)

        self.assertEqual(
            payroll.amount,
            Decimal('9.90'),
        )

        self.assertEqual(
            payroll.sessions_90,
            1,
        )

    def test_two_late_hours_get_two_percent_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        self.create_report(
            session,
            total_late_hours=2,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        # 10 * 0.98 = 9.80
        self.assertEqual(
            payroll.amount,
            Decimal('9.80'),
        )

    def test_late_hours_are_accumulated_in_payroll_penalty(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        self.create_report(
            session,
            total_late_hours=4,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            payroll.amount,
            Decimal('9.60'),
        )

    def test_late_penalty_can_reduce_wage_to_zero(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        self.create_report(
            session,
            total_late_hours=100,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            payroll.amount,
            Decimal(0),
        )

        self.assertEqual(
            payroll.sessions_90,
            1,
        )

    def test_summer_term_applies_summer_term_multiplier(self):
        summer_term = Term.objects.create(
            start_date=date(2027, 6, 1),
            end_date=date(2027, 8, 31),
            type='summer',
        )

        summer_course = Course.objects.create(
            school=self.school,
            term=summer_term,
            subject='Summer Python',
            duration=90,
        )

        CourseTeacher.objects.create(
            course_obj=summer_course,
            teacher=self.teacher,
            start_date=date(2027, 6, 1),
            end_date=date(2027, 8, 31),
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=summer_term,
            base_rate=Decimal(10),
        )

        session = self.create_session(
            summer_course,
            1,
            date(2027, 6, 5),
        )

        self.create_report(session)

        payroll = calculate_teacher_payroll(
            self.teacher,
            2027,
            6,
        )

        self.assertEqual(
            payroll.amount,
            Decimal(11),
        )

    def test_summer_multiplier_is_applied_after_late_penalty(self):
        summer_term = Term.objects.create(
            start_date=date(2027, 6, 1),
            end_date=date(2027, 8, 31),
            type='summer',
        )

        summer_course = Course.objects.create(
            school=self.school,
            term=summer_term,
            subject='Summer Python',
            duration=90,
        )

        CourseTeacher.objects.create(
            course_obj=summer_course,
            teacher=self.teacher,
            start_date=date(2027, 6, 1),
            end_date=date(2027, 8, 31),
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=summer_term,
            base_rate=Decimal(10),
        )

        session = self.create_session(
            summer_course,
            1,
            date(2027, 6, 5),
        )

        self.create_report(
            session,
            total_late_hours=1,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2027,
            6,
        )

        self.assertEqual(
            payroll.amount,
            Decimal('10.89'),
        )

    def test_recalculating_same_month_replaces_previous_payroll(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        self.create_report(session)

        first_payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            first_payroll.amount,
            Decimal(10),
        )

        second_session = self.create_session(
            self.course_90,
            2,
            date(2026, 9, 6),
        )

        self.create_report(second_session)

        second_payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertEqual(
            second_payroll.amount,
            Decimal(20),
        )

        self.assertEqual(
            PayrollRecord.objects.filter(
                teacher=self.teacher,
                year=2026,
                month=9,
            ).count(),
            1,
        )

    def test_teacher_without_approved_reports_has_no_payroll_record(self):
        session = self.create_session(
            self.course_90,
            1,
            date(2026, 9, 5),
        )

        self.create_report(
            session,
            SessionReport.Status.PENDING,
        )

        payroll = calculate_teacher_payroll(
            self.teacher,
            2026,
            9,
        )

        self.assertIsNone(payroll)

        self.assertFalse(
            PayrollRecord.objects.filter(
                teacher=self.teacher,
                year=2026,
                month=9,
            ).exists()
        )
from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from payroll.models import PayrollRecord, TeacherTermRate
from users.models import User


class PayrollRecordViewTests(APITestCase):
    def setUp(self):
        self.finance_officer = User.objects.create_user(
            username='test_finance',
            password='pass789',
            role='finance_officer',
        )

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='=+989123456789',
            emergency_number='+989876543210'
        )

        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='=+981234567890',
            emergency_number='+989123456789'
        )

        self.payroll = PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=9,
            amount=Decimal(30),
        )

        self.payroll2 = PayrollRecord.objects.create(
            teacher=self.teacher2,
            year=2026,
            month=9,
            amount=Decimal(40),
        )

    def test_finance_officer_can_see_monthly_payrolls(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.get(
            reverse('payroll-monthly-list'),
            {
                'year': 2026,
                'month': 9,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_teacher_cannot_see_monthly_payroll_list(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            reverse('payroll-monthly-list'),
            {
                'year': 2026,
                'month': 9,
            },
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_teacher_can_see_only_own_payroll_history(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            reverse('teacher-payroll-history')
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]['teacher'],
            self.teacher.id,
        )

    def test_finance_officer_cannot_access_teacher_history(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.get(
            reverse('teacher-payroll-history')
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_finance_officer_can_calculate_all_teachers(self):
        school = School.objects.create(
            name='School B',
            address='Address B',
        )

        term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
            type='regular',
        )

        course = Course.objects.create(
            school=school,
            term=term,
            subject='Python',
            duration=90,
        )

        CourseTeacher.objects.create(
            course_obj=course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

        CourseTeacher.objects.create(
            course_obj=course,
            teacher=self.teacher2,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=term,
            base_rate=Decimal(10),
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher2,
            term=term,
            base_rate=Decimal(15),
        )

        session_1 = Session.objects.create(
            course_obj=course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        SessionReport.objects.create(
            session=session_1,
            teacher=self.teacher,
            summary='Teacher 1 report',
            present_count=10,
            absent_count=0,
            status=SessionReport.Status.APPROVED,
        )

        session_2 = Session.objects.create(
            course_obj=course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        SessionReport.objects.create(
            session=session_2,
            teacher=self.teacher2,
            summary='Teacher 2 report',
            present_count=10,
            absent_count=0,
            status=SessionReport.Status.APPROVED,
        )

        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            reverse('payroll-calculate-all'),
            {
                'year': 2026,
                'month': 9,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            PayrollRecord.objects.filter(
                year=2026,
                month=9,
            ).count(),
            2,
        )
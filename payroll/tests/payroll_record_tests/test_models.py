from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from payroll.models import PayrollRecord
from users.models import User


class PayrollRecordModelTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )

    def test_payroll_record_can_be_created(self):
        payroll = PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=8,
            amount=Decimal(127),
            sessions_60=2,
            sessions_90=10,
            sessions_120=1,
        )

        self.assertEqual(payroll.teacher, self.teacher)
        self.assertEqual(payroll.year, 2026)
        self.assertEqual(payroll.month, 8)
        self.assertEqual(payroll.amount, Decimal(127))

    def test_payroll_record_has_unique_teacher_and_month(self):
        PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=8,
            amount=Decimal(127),
        )

        with self.assertRaises(IntegrityError):
            PayrollRecord.objects.create(
                teacher=self.teacher,
                year=2026,
                month=8,
                amount=Decimal(150),
            )

    def test_same_teacher_can_have_payroll_for_different_months(self):
        PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=8,
            amount=Decimal(127),
        )

        second_payroll = PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=10,
            amount=Decimal(150),
        )

        self.assertEqual(second_payroll.month, 10)

    def test_different_teachers_can_have_payroll_for_same_month(self):
        teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='=+981234567890',
            emergency_number='+989123456789'
        )

        PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=8,
            amount=Decimal(127),
        )

        payroll2 = PayrollRecord.objects.create(
            teacher=teacher2,
            year=2026,
            month=8,
            amount=Decimal(150),
        )

        self.assertEqual(payroll2.teacher, teacher2)

    def test_breakdown_defaults_to_zero(self):
        payroll = PayrollRecord.objects.create(
            teacher=self.teacher,
            year=1405,
            month=5,
            amount=Decimal(0),
        )

        self.assertEqual(payroll.sessions_60, 0)
        self.assertEqual(payroll.sessions_90, 0)
        self.assertEqual(payroll.sessions_120, 0)
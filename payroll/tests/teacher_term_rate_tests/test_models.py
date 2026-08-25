from datetime import date
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from education.models import School, Term
from payroll.models import TeacherTermRate
from users.models import User


class TeacherTermRateModelTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher A',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )

        self.school = School.objects.create(
            name='School A',
            address='Address A',
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
            type='regular',
        )

    def test_teacher_term_rate_can_be_created(self):
        rate = TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        self.assertEqual(rate.teacher, self.teacher)
        self.assertEqual(rate.term, self.term)
        self.assertEqual(rate.base_rate, Decimal(10))

    def test_teacher_term_rate_has_unique_teacher_and_term(self):
        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        with self.assertRaises(IntegrityError):
            TeacherTermRate.objects.create(
                teacher=self.teacher,
                term=self.term,
                base_rate=Decimal(15),
            )

    def test_same_teacher_can_have_rate_for_different_terms(self):
        self.term2 = Term.objects.create(
            start_date=date(2027, 2, 1),
            end_date=date(2027, 4, 30),
            type='regular',
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        second_rate = TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term2,
            base_rate=Decimal(15),
        )

        self.assertEqual(second_rate.base_rate, Decimal(15))

    def test_different_teachers_can_have_rate_for_same_term(self):
        teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='=+981234567890',
            emergency_number='+989123456789'
        )

        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        rate2 = TeacherTermRate.objects.create(
            teacher=teacher2,
            term=self.term,
            base_rate=Decimal(15),
        )

        self.assertEqual(rate2.teacher, teacher2)

    def test_str_returns_expected_value(self):
        rate = TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

        self.assertEqual(
            str(rate),
            f"{self.teacher} - {self.term} - 10",
        )
from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from education.models import School, Term
from payroll.models import TeacherTermRate
from users.models import User


class TeacherTermRateViewTests(APITestCase):
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
            phone_number='+989123456789',
            emergency_number='+989876543210'
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

    def test_finance_officer_can_create_rate(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.post(
            reverse('teacher-term-rate-list-create'),
            {
                'teacher': self.teacher.id,
                'term': self.term.id,
                'base_rate': '15',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            TeacherTermRate.objects.filter(
                teacher=self.teacher,
                term=self.term,
                base_rate=Decimal(15),
            ).exists()
        )

    def test_teacher_cannot_create_rate(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            reverse('teacher-term-rate-list-create'),
            {
                'teacher': self.teacher.id,
                'term': self.term.id,
                'base_rate': '15',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_finance_officer_can_list_rates(self):
        TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(15),
        )

        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.get(
            reverse('teacher-term-rate-list-create')
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )
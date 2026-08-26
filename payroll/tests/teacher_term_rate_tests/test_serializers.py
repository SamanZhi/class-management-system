from datetime import date
from decimal import Decimal

from django.test import TestCase

from education.models import School, Term
from payroll.models import TeacherTermRate
from payroll.serializers import TeacherTermRateSerializer
from users.models import User


class TeacherTermRateSerializerTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123',
            role='teacher',
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

        self.rate = TeacherTermRate.objects.create(
            teacher=self.teacher,
            term=self.term,
            base_rate=Decimal(10),
        )

    def test_serializes_teacher_term_rate(self):
        serializer = TeacherTermRateSerializer(self.rate)

        self.assertEqual(
            serializer.data['teacher'],
            self.teacher.id,
        )
        self.assertEqual(
            serializer.data['term'],
            self.term.id,
        )
        self.assertEqual(
            Decimal(serializer.data['base_rate']),
            Decimal(10),
        )

    def test_creates_teacher_term_rate(self):
        serializer = TeacherTermRateSerializer(
            data={
                'teacher': self.teacher.id,
                'term': self.term.id,
                'base_rate': '15',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        rate = serializer.save()

        self.assertEqual(rate.teacher, self.teacher)
        self.assertEqual(rate.term, self.term)
        self.assertEqual(rate.base_rate, Decimal(15))

    def test_id_is_read_only(self):
        serializer = TeacherTermRateSerializer(
            instance=self.rate,
            data={
                'id': 999,
                'teacher': self.teacher.id,
                'term': self.term.id,
                'base_rate': '20',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated_rate = serializer.save()

        self.assertEqual(updated_rate.id, self.rate.id)
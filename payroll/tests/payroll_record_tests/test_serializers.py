from decimal import Decimal

from django.test import TestCase

from payroll.models import PayrollRecord
from payroll.serializers import PayrollRecordSerializer
from users.models import User


class PayrollRecordSerializerTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass123',
            role='teacher',
        )

        self.payroll = PayrollRecord.objects.create(
            teacher=self.teacher,
            year=2026,
            month=9,
            amount=Decimal('25.50'),
            sessions_60=2,
            sessions_90=1,
            sessions_120=1,
        )

    def test_serializes_payroll_record(self):
        serializer = PayrollRecordSerializer(
            self.payroll
        )

        self.assertEqual(
            serializer.data['teacher'],
            self.teacher.id,
        )
        self.assertEqual(
            serializer.data['year'],
            2026,
        )
        self.assertEqual(
            serializer.data['month'],
            9,
        )
        self.assertEqual(
            Decimal(serializer.data['amount']),
            Decimal('25.50'),
        )

    def test_payroll_record_fields_are_read_only(self):
        serializer = PayrollRecordSerializer(
            instance=self.payroll,
            data={
                'teacher': self.teacher.id,
                'year': 2027,
                'month': 10,
                'amount': '100',
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated_payroll = serializer.save()

        self.assertEqual(
            updated_payroll.teacher,
            self.teacher,
        )
        self.assertEqual(
            updated_payroll.year,
            2026,
        )
        self.assertEqual(
            updated_payroll.month,
            9,
        )
        self.assertEqual(
            updated_payroll.amount,
            Decimal('25.50'),
        )

    def test_breakdown_fields_are_not_in_output(self):
        serializer = PayrollRecordSerializer(self.payroll)

        self.assertNotIn(
            'sessions_60',
            serializer.data,
        )
        self.assertNotIn(
            'sessions_90',
            serializer.data,
        )
        self.assertNotIn(
            'sessions_120',
            serializer.data,
        )
from datetime import date

from django.test import TestCase

from education.models import Term
from education.serializers.term import TermSerializer


class TermSerializerTests(TestCase):
    def create_term(
            self,
            start_date=date(2026, 9, 1), 
            end_date=date(2026, 11, 30), 
            term_type='regular'):
        return Term.objects.create(start_date=start_date, end_date=end_date, type=term_type)

    def test_serialized_fields(self):
        term = self.create_term()

        data = TermSerializer(term).data

        self.assertEqual(
            set(data.keys()),
            {
                'id',
                'start_date',
                'end_date',
                'type',
                'is_deleted',
                'created_at',
                'updated_at'
            },
        )

    def test_read_only_fields(self):
        term = self.create_term()
        
        serializer = TermSerializer(term)

        self.assertEqual(
                    set(serializer.Meta.read_only_fields),
                    {
                        'id',
                        'is_deleted',
                        'created_at',
                        'updated_at'
                    },
                )

    def test_valid_term_data(self):
        data = {
            'start_date': '2026-09-01',
            'end_date': '2026-11-30',
            'type': 'regular'
        }

        serializer = TermSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_start_date_must_be_first_day_of_month(self):
        data = {
            'start_date': '2026-09-15',
            'end_date': '2026-11-30',
            'type': 'regular'
        }

        serializer = TermSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('start_date', serializer.errors)

    def test_start_date_on_first_day_of_month_is_valid(self):
        data = {
            'start_date': '2026-09-01',
            'end_date': '2026-11-30',
            'type': 'regular'
        }

        serializer = TermSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_end_date_must_be_after_start_date(self):
        data = {
            'start_date': '2026-09-01',
            'end_date': '2026-08-01',
            'type': 'regular'
        }

        serializer = TermSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_invalid_term_type_is_rejected(self):
        data = {
            'start_date': '2026-09-01',
            'end_date': '2026-10-30',
            'type': 'winter'
        } 

        serializer = TermSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('type', serializer.errors)

    def test_overlapping_term_is_rejected(self):
        self.create_term(start_date=date(2026, 7, 1), end_date=date(2026, 9, 30))

        data = {
            'start_date': '2026-08-01',
            'end_date': '2026-09-15',
            'type': 'regular'
        }

        serializer = TermSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('start_date', serializer.errors)

    def test_updating_term_does_not_conflict_with_itself(self):
        term = self.create_term()

        data = {
                'start_date': '2026-09-01',
                'end_date': '2026-10-30',
                'type': 'regular'
            }

        serializer = TermSerializer(term, data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
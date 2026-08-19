from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from education.models import Term


class TermModelTest(TestCase):
    def create_term(self, start_date=date(2026, 9, 1), end_date=date(2026, 11, 31), term_type='regular'):
        return Term.objects.create(start_date=start_date, end_date=end_date, type=term_type)

    def test_create_term(self):
        term = self.create_term()

        self.assertEqual(term.start_date, date(2026, 9, 1))
        self.assertEqual(term.end_date, date(2026, 11, 31))
        self.assertEqual(term.type, 'regular')
        self.assertFalse(term.is_deleted)
        self.assertIsNone(term.deleted_at)


    def test_str_returns_term_type_and_dates(self):
        term = self.create_term()

        self.assertEqual(str(term), 'regular - (2026-09-01 to 2026-11-31)')

    def test_end_date_must_be_after_start_date(self):
        term = Term(start_date=date(2026, 11, 20), end_date=date(2026, 10, 10), type='regular')

        with self.assertRaises(ValidationError):
            term.full_clean()

    def test_terms_cannot_overlap(self):
        self.create_term(start_date=date(2026, 9, 1), end_date=date(2026, 11, 31))

        overlapping_term = Term(start_date=date(2026, 9, 10), end_date=date(2026, 10, 31), type='regular')

        with self.assertRaises(ValidationError):
            overlapping_term.full_clean()

    def test_term_ending_on_existing_start_date_cannot_overlap(self):
        self.create_term(start_date=date(2026, 10, 1), end_date=date(2026, 11, 31))
        
        overlapping_term = Term(start_date=date(2026, 9, 1), end_date=date(2026, 10, 1), type='regular')

        with self.assertRaises(ValidationError):
            overlapping_term.full_clean()

    def test_non_overlapping_terms_are_valid(self):
        self.create_term(start_date=date(2026, 9, 1), end_date=date(2026, 10, 10))

        second_term = Term(start_date=date(2026, 10, 15), end_date=date(2026, 12, 25), type='regular')

        second_term.full_clean()

    def test_summer_term_can_be_created(self):
        term = self.create_term(start_date=date(2027, 6, 1), end_date=date(2027, 6, 30), type='summer')

        self.assertEqual(term.type, 'summer')

    def test_soft_delete_sets_is_deleted_and_deleted_at(self):
        term = self.create_term()

        before=timezone.now()

        term.soft_delete()
        term.refresh_from_db()

        self.assertTrue(term.is_deleted)
        self.assertIsNotNone(term.deleted_at)
        self.assertGreaterEqual(term.deleted_at, before)

    def test_soft_deleted_term_is_excluded_from_default_manager(self):
        term = self.create_term()

        term.soft_delete()

        self.assertFalse(Term.objects.filter(pk=term.pk).exists())

    def test_soft_deleted_term_is_visible_in_all_objects_manager(self):
        term = self.create_term()

        term.soft_delete()

        deleted_term = Term.all_objects.get(pk=term.pk)

        self.assertTrue(deleted_term.is_deleted)
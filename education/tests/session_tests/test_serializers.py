from datetime import date

from django.test import TestCase

from education.models import Course, School, Session, Term
from education.serializers.session import SessionSerializer


class SessionSerializerTests(TestCase):

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

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )

    def test_valid_session_data(self):
        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-05',
        }

        serializer = SessionSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_session_before_term_is_invalid(self):
        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-08-31',
        }

        serializer = SessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

    def test_session_after_term_is_invalid(self):
        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-12-10',
        }

        serializer = SessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

    def test_duplicate_session_number_is_invalid(self):
        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-06',
        }

        serializer = SessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'non_field_errors',
            serializer.errors,
        )

    def test_duplicate_session_date_is_invalid(self):
        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 2,
            'date': '2026-09-05',
        }

        serializer = SessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

    def test_required_fields_are_required(self):
        serializer = SessionSerializer(data={})

        self.assertFalse(serializer.is_valid())

        self.assertIn('course_obj', serializer.errors)
        self.assertIn('session_number', serializer.errors)
        self.assertIn('date', serializer.errors)

    def test_updating_existing_session_does_not_conflict_with_itself(self):
        session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-05',
        }

        serializer = SessionSerializer(
            session,
            data=data,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
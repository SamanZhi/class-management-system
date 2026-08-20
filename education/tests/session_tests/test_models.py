from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from education.models import Course, School, Session, Term
from users.models import User


class SessionModelTests(TestCase):

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

    def test_create_session(self):
        session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        self.assertEqual(session.course_obj, self.course)
        self.assertEqual(session.session_number, 1)
        self.assertEqual(session.date, date(2026, 9, 5))
        self.assertFalse(session.is_deleted)
        self.assertIsNone(session.deleted_at)

    def test_session_date_must_be_inside_term(self):
        session = Session(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 8, 31),
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_date_cannot_be_after_term(self):
            session = Session(
                course_obj=self.course,
                session_number=1,
                date=date(2026, 12, 10),
            )

            with self.assertRaises(ValidationError):
                session.full_clean()

    def test_session_number_must_be_unique_for_course(self):
        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        duplicate = Session(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 6),
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_session_number_is_allowed_for_different_courses(self):
        course2 = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Django',
            duration=120,
        )

        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        session2 = Session(
            course_obj=course2,
            session_number=1,
            date=date(2026, 9, 5),
        )

        session2.full_clean()

    def test_two_sessions_of_same_course_cannot_have_same_date(self):
        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        duplicate = Session(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 5),
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_course_can_have_sessions_on_different_dates(self):
        Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        session2 = Session(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        session2.full_clean()

    def test_soft_delete_sets_deleted_fields(self):
        session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        before = timezone.now()

        session.soft_delete()
        session.refresh_from_db()

        self.assertTrue(session.is_deleted)
        self.assertIsNotNone(session.deleted_at)
        self.assertGreaterEqual(session.deleted_at, before)

    def test_soft_deleted_session_is_excluded_from_default_manager(self):
        session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        session.soft_delete()

        self.assertFalse(
            Session.objects.filter(pk=session.pk).exists()
        )

    def test_soft_deleted_session_is_visible_in_all_objects(self):
        session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        session.soft_delete()

        self.assertTrue(
            Session.all_objects.filter(pk=session.pk).exists()
        )
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from education.models import Course, CourseTeacher, School, Term
from users.models import User


class CourseModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='School A', address='Address A')

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 31),
            type='regular'
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90
        )

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='=+989123456789',
            emergency_number='+989876543210'
        )

    def test_create_course(self):
        self.assertEqual(self.course.school, self.school)
        self.assertEqual(self.course.term, self.term)
        self.assertEqual(self.course.subject, 'Python')
        self.assertEqual(self.course.duration, 90)
        self.assertFalse(self.course.is_deleted)
        self.assertIsNone(self.course.deleted_at)

    def test_str_returns_expected_value(self):
        self.assertEqual(str(self.course), 'Python (90min) - regular - (2026-09-01 to 2026-11-31)')

    def test_valid_course_durations(self):
        for duration in [60, 90, 120]:
            course = Course(
                school=self.school,
                term=self.term,
                subject='English',
                duration=duration
            )

            course.full_clean()

    def test_invalid_course_duration_is_rejected(self):
        course = Course(
            school=self.school,
            term=self.term,
            subject='English',
            duration=45
        )

        with self.assertRaises(ValidationError)
            course.full_clean()
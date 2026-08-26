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
            end_date=date(2026, 11, 30),
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
            phone_number='+989123456789',
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
        self.assertEqual(str(self.course), 'Python (90min) - regular - (2026-09-01 to 2026-11-30)')

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

        with self.assertRaises(ValidationError):
            course.full_clean()

    def test_soft_delete_sets_deleted_fields(self):
        before = timezone.now()
        
        self.course.soft_delete()
        self.course.refresh_from_db()

        self.assertTrue(self.course.is_deleted)
        self.assertIsNotNone(self.course.deleted_at)
        self.assertGreaterEqual(self.course.deleted_at, before)

    def test_soft_deleted_course_is_excluded_from_default_manager(self):
        self.course.soft_delete()

        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

    def test_soft_deleted_course_is_visible_in_all_objects_manager(self):
        self.course.soft_delete()

        self.assertTrue(Course.all_objects.filter(pk=self.course.pk).exists())     


class CourseTeacherModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='School B', address='Address B')

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 20),
            type='regular'
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=120
        )

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210'
        )

        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='+981234567890',
            emergency_number='+989123456789'
        )

    def test_create_course_teacher_assignment(self):
        assignment = CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 1)
        )

        self.assertEqual(assignment.course_obj, self.course)
        self.assertEqual(assignment.teacher, self.teacher)
        self.assertEqual(assignment.start_date, date(2026, 9, 1))
        self.assertEqual(assignment.end_date, date(2026, 11, 1))

    def test_end_date_must_be_after_start_date(self):
        assignment = CourseTeacher(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 1)            
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_assignment_start_date_must_be_inside_term(self):
        assignment = CourseTeacher(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 8, 25),
            end_date=date(2026, 9, 15)            
        )

        with self.assertRaises(ValidationError):
                    assignment.full_clean()

    def test_assignment_end_date_must_be_inside_term(self):
        assignment = CourseTeacher(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 10, 25),
            end_date=date(2026, 12, 25)            
        )

        with self.assertRaises(ValidationError):
                    assignment.full_clean()

    def test_assignment_can_have_no_end_date(self):
        assignment = CourseTeacher(
        course_obj= self.course,
        teacher=self.teacher,
        start_date=date(2026, 10, 25)           
        )

        assignment.full_clean()

    def test_overlapping_assignments_are_rejected(self):
        CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 25),
            end_date=date(2026, 11, 25) 
        )

        overlapping = CourseTeacher(
            course_obj= self.course,
            teacher=self.teacher2,
            start_date=date(2026, 10, 25),
            end_date=date(2026, 11, 15) 
        )

        with self.assertRaises(ValidationError):
             overlapping.full_clean()

    def test_non_overlapping_assignments_are_valid(self):
        CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 25) 
        )

        assignment = CourseTeacher(
            course_obj= self.course,
            teacher=self.teacher2,
            start_date=date(2026, 10, 26),
            end_date=date(2026, 11, 25) 
        )

        assignment.full_clean()

    def test_soft_delete_assignment(self):
        assignment = CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 25) 
        )

        assignment.soft_delete()
        assignment.refresh_from_db()

        self.assertTrue(assignment.is_deleted)
        self.assertIsNotNone(assignment.deleted_at)

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from education.models import Course, CourseTeacher, School, Term
from education.serializers.course import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseTeacherSerializer,
)
from users.models import User


class CourseSerializerTests(TestCase):
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

    def test_serialized_fields(self):
        data = CourseSerializer(self.course).data

        self.assertEqual(
            set(data.keys()), 
            {
                'id',
                'school',
                'term',
                'subject',
                'duration',
                'is_deleted',
                'created_at',
                'updated_at'
            }
        )

    def test_valid_course_data(self):
        data = {
            'school': self.school.id,
            'term': self.term.id,
            'subject': 'Django',
            'duration': 120
        }

        serializer = CourseSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors
        )

    def test_invalid_duration_is_rejected(self):
        data = {
            'school': self.school.id,
            'term': self.term.id,
            'subject': 'Django',
            'duration': 45
        }

        serializer = CourseSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('duration', serializer.errors)

    def test_invalid_school_is_rejected(self):
        data = {
            'school': 99999,
            'term': self.term.id,
            'subject': 'Django',
            'duration': 90
        }

        serializer = CourseSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('school', serializer.errors)

    def test_invalid_term_is_rejected(self):
        data = {
            'school': self.school.id,
            'term': 99999,
            'subject': 'Django',
            'duration': 90
        }

        serializer = CourseSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('term', serializer.errors)


class CourseTeacherSerializerTests(TestCase):
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

        
        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='+981234567890',
            emergency_number='+989123456789'
        )

    def test_serialized_fields(self):
        assignment = CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 30)
        )

        data = CourseTeacherSerializer(assignment).data

        self.assertEqual(
            set(data.keys()), 
            {
                'id',
                'course_obj',
                'teacher',
                'start_date',
                'end_date',
                'created_at',
                'updated_at'
            }
        )

    def test_only_teacher_role_users_are_valid_for_assignment(self):
        non_teacher = User.objects.create_user(
            username='test_edu_officer',
            password='pass123',
            role='education_officer',
        )

        data = {
            'course_obj': self.course.id,
            'teacher': non_teacher.id,
            'start_date': '2026-09-01',
            'end_date': '2026-11-01',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('teacher', serializer.errors)

    def test_valid_assignment_data(self):
        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher.id,
            'start_date': '2026-09-01',
            'end_date': '2026-11-01',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(), 
            serializer.errors
        )

    def test_end_date_before_start_date_is_rejected(self):
        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher.id,
            'start_date': '2026-09-20',
            'end_date': '2026-09-01',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_start_date_before_term_is_rejected(self):
        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher.id,
            'start_date': '2026-08-30',
            'end_date': '2026-11-01',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('start_date', serializer.errors)

    def test_end_date_after_term_is_rejected(self):
        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher.id,
            'start_date': '2026-09-01',
            'end_date': '2026-12-01',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_overlapping_assignment_is_rejected(self):
        CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 1)  
        )

        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher2.id,
            'start_date': '2026-09-15',
            'end_date': '2026-10-30',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_non_overlapping_assignment_is_valid(self):
        CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 25)  
        )

        data = {
            'course_obj': self.course.id,
            'teacher': self.teacher2.id,
            'start_date': '2026-10-30',
            'end_date': '2026-11-25',
        }

        serializer = CourseTeacherSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(), 
            serializer.errors
        )


class CourseDetailsSerializerTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='School A', address='Address A')

        self.term = Term.objects.create(
            start_date=date(2026, 8, 1),
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
            username='saman_teacher',
            password='pass123',
            role='teacher',
            first_name='Saman',
            last_name='Zhiani',
            phone_number='+989361208772',
            emergency_number='+989876543210'
        )

    def test_current_teacher_is_returned(self):
        today = timezone.now().date()

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10)
        )

        data = CourseDetailSerializer(self.course).data

        self.assertIsNotNone(data['current_teacher'])
        self.assertEqual(data['current_teacher']['id'], self.teacher.id)
        self.assertEqual(
            data['current_teacher']['first_name'],
            'Saman'
        )
        self.assertEqual(
            data['current_teacher']['last_name'],
            'Zhiani'
        )
        self.assertEqual(
            data['current_teacher']['phone_number'],
            '+989361208772'
        )

    def test_current_teacher_is_none_when_no_active_assignment(self):
        data = CourseDetailSerializer(self.course).data

        self.assertIsNone(data['current_teacher'])

    def test_only_current_teacher_is_returned(self):
        today = timezone.now().date()

        previous_teacher = User.objects.create_user(
            username='previous_teacher',
            password='pass123',
            role='teacher',
            first_name='Previous',
            last_name='Teacher',
            phone_number='+981111111111',
            emergency_number='+982222222222'
        )

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=previous_teacher,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=5)
        )

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=today - timedelta(days=4),
            end_date=None
        )

        data = CourseDetailSerializer(self.course).data

        self.assertEqual(
            data['current_teacher']['id'],
            self.teacher.id
        )

        self.assertNotEqual(
            data['current_teacher']['id'],
            previous_teacher.id
        )

    def test_future_teacher_is_not_returned_as_current_teacher(self):
        today = timezone.now().date()

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=today + timedelta(days=10),
            end_date=None
        )

        data = CourseDetailSerializer(self.course).data

        self.assertIsNone(data['current_teacher'])
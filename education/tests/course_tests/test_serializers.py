from datetime import date

from django.test import TestCase
from django.utils import timezone

from education.models import Course, CourseTeacher, School, Term
from education.serializers import (
    CourseDetailSerializer,
    CourseSerializer,
    CourseTeacherSerializer
)
from users.models import User


class CourseSerializerTests(TestCase):
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
            'school': self.school,
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

        
        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='=+981234567890',
            emergency_number='+989123456789'
        )

    def test_serialized_fields(self):
        assignment = CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30)
        )

        data = CourseTeacherSerializer(assignment).data

        self.assertEqual(
            set(data.keys()), 
            {
                'id',
                'course_obg=j',
                'teacher',
                'start_date',
                'end_date',
                'created_at',
                'updated_at'
            }
        )
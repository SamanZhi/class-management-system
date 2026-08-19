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
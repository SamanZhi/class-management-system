from django.test import TestCase
from django.utils import timezone

from schools.models import School


class SchoolModelTest(TestCase):
    def test_create_school(self):
        school = School.objects.create(name='Derakshan', address='Mashhad')
        self.assertEqual(school.name, 'Derakhshan')
        self.assertFalse(school.is_deleted)
        self.assertIsNone(school.deleted_at)

    def test_str_returns_name(self):
        school = School.objects.create(name='School A')
        self.assertEqual(str(school), 'School A')
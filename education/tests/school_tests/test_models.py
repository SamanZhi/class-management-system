from django.test import TestCase
from django.utils import timezone

from education.models import School


class SchoolModelTest(TestCase):
    def test_create_school(self):
        school = School.objects.create(name='School A', address='City A')
        self.assertEqual(school.name, 'School A')
        self.assertFalse(school.is_deleted)
        self.assertIsNone(school.deleted_at)

    def test_str_returns_name(self):
        school = School.objects.create(name='School B')
        self.assertEqual(str(school), 'School B')

    def test_soft_delete_sets_is_deleted_and_deleted_at(self):
        school = School.objects.create(name='School C')
        before = timezone.now()
        school.soft_delete()
        school.refresh_from_db()

        self.assertTrue(school.is_deleted)
        self.assertIsNotNone(school.deleted_at)
        self.assertGreaterEqual(school.deleted_at, before)

    def test_soft_deleted_excluded_from_default_manager(self):
        school = School.objects.create(name='School D')
        school.soft_delete()

        self.assertNotIn(school, School.objects.all())
        self.assertEqual(School.objects.filter(pk=school.pk).count(), 0)

    def test_soft_deleted_visible_in_all_objects_manager(self):
        school = School.objects.create(name='School E')
        school.soft_delete()

        self.assertIn(school, School.all_objects.all())
        self.assertTrue(School.all_objects.get(pk=school.pk).is_deleted)
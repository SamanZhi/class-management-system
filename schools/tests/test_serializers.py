from django.test import TestCase

from schools.models import School
from schools.serializers import SchoolSerializer


class SchoolSerializerTests(TestCase):
    def test_serialized_fields(self):
        school = School.objects.create(name='School A', address='City A')
        data = SchoolSerializer(school).data
        self.assertEqual(set(data.keys()), {'id', 'name', 'is_deleted', 'created_at', 'updated_at'})



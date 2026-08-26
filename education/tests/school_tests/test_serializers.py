from django.test import TestCase

from education.models import School
from education.serializers.school import SchoolSerializer


class SchoolSerializerTests(TestCase):
    def test_serialized_fields(self):
        school = School.objects.create(name='School A', address='City A')
        data = SchoolSerializer(school).data
        self.assertEqual(set(data.keys()), {'id', 'name', 'address', 'is_deleted', 'created_at', 'updated_at'})



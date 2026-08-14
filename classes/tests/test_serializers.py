
from django.test import TestCase

from classes.models import Class, ClassTeacher
from classes.serializers import ClassSerializer, ClassTeacherSerializer
from schools.models import School
from terms.models import Term
from users.models import User


def make_school():
    return School.objects.create(name='مدرسه تست')


def make_term():
    return Term.objects.create(
        start_date='2024-01-01',
        end_date='2024-06-30',
        term_type='regular',
    )


def make_class(school, term):
    return Class.objects.create(school=school, term=term, subject='ریاضی', duration=60)


def make_teacher(username='t1'):
    return User.objects.create_user(
        username=username,
        password='pass',
        role='teacher',
        phone_number='+989111111111',
        emergency_number='+989222222222',
    )


class ClassSerializerTests(TestCase):
    def setUp(self):
        self.school = make_school()
        self.term = make_term()
        self.cls = make_class(self.school, self.term)

    def test_fields_present(self):
        data = ClassSerializer(self.cls).data
        expected = {'id', 'school', 'term', 'subject', 'duration', 'is_deleted', 'created_at', 'updated_at'}
        self.assertEqual(set(data.keys()), expected)

    def test_create_via_serializer(self):
        data = {
            'school': self.school.id,
            'term': self.term.id,
            'subject': 'شیمی',
            'duration': 90,
        }
        s = ClassSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        obj = s.save()
        self.assertEqual(obj.subject, 'شیمی')

    def test_invalid_duration(self):
        data = {
            'school': self.school.id,
            'term': self.term.id,
            'subject': 'شیمی',
            'duration': 45,
        }
        s = ClassSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('duration', s.errors)


class ClassTeacherSerializerTests(TestCase):
    def setUp(self):
        self.school = make_school()
        self.term = make_term()
        self.cls = make_class(self.school, self.term)
        self.teacher = make_teacher('t1')
        self.teacher2 = make_teacher('t2')

    def _post_data(self, start, end=None, teacher=None, cls=None):
        return {
            'class_obj': (cls or self.cls).id,
            'teacher': (teacher or self.teacher).id,
            'start_date': start,
            'end_date': end,
        }

    def test_end_before_start_invalid(self):
        s = ClassTeacherSerializer(data=self._post_data('2024-05-01', '2024-04-01'))
        self.assertFalse(s.is_valid())
        self.assertIn('end_date', s.errors)

    def test_end_same_as_start_valid_in_serializer(self):
        s = ClassTeacherSerializer(data=self._post_data('2024-03-01', '2024-03-01'))
        if s.is_valid():
            with self.assertRaises(Exception):
                obj = s.save()
                obj.full_clean()

    def test_valid_assignment(self):
        s = ClassTeacherSerializer(data=self._post_data('2024-01-01', '2024-06-30'))
        self.assertTrue(s.is_valid(), s.errors)

    def test_open_ended_valid(self):
        s = ClassTeacherSerializer(data=self._post_data('2024-01-01', None))
        self.assertTrue(s.is_valid(), s.errors)

    def test_overlap_rejected_by_serializer(self):
        ClassTeacher.objects.create(
            class_obj=self.cls,
            teacher=self.teacher,
            start_date='2024-01-01',
            end_date='2024-06-30',
        )
        s = ClassTeacherSerializer(data=self._post_data('2024-03-01', '2024-08-31', teacher=self.teacher2))
        self.assertFalse(s.is_valid())

    def test_no_overlap_adjacent_valid(self):
        ClassTeacher.objects.create(
            class_obj=self.cls,
            teacher=self.teacher,
            start_date='2024-01-01',
            end_date='2024-03-31',
        )
        s = ClassTeacherSerializer(data=self._post_data('2024-04-01', '2024-06-30', teacher=self.teacher2))
        self.assertTrue(s.is_valid(), s.errors)

    def test_update_excludes_self_from_overlap_check(self):
        ct = ClassTeacher.objects.create(
            class_obj=self.cls,
            teacher=self.teacher,
            start_date='2024-01-01',
            end_date='2024-06-30',
        )
        s = ClassTeacherSerializer(
            instance=ct,
            data={'end_date': '2024-05-31'},
            partial=True,
        )
        self.assertTrue(s.is_valid(), s.errors)

    def test_non_teacher_role_rejected(self):
        admin = User.objects.create_user(
            username='admin1',
            password='pass',
            role='education_officer',
        )
        s = ClassTeacherSerializer(data={
            'class_obj': self.cls.id,
            'teacher': admin.id,
            'start_date': '2024-01-01',
        })
        self.assertFalse(s.is_valid())
        self.assertIn('teacher', s.errors)

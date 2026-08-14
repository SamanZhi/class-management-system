from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from classes.models import Class, ClassTeacher
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


def make_class(school, term, subject='ریاضی'):
    return Class.objects.create(school=school, term=term, subject=subject, duration=60)


class ClassViewsTestCase(APITestCase):
    def setUp(self):
        self.school = make_school()
        self.term = make_term()
        self.cls = make_class(self.school, self.term)

        self.edu = User.objects.create_user(
            username='edu', password='pass', role='education_officer'
        )
        self.finance = User.objects.create_user(
            username='finance', password='pass', role='finance_officer'
        )
        self.teacher = User.objects.create_user(
            username='teacher', password='pass', role='teacher',
            phone_number='+989111111111', emergency_number='+989222222222',
        )

        self.list_url = reverse('classes:class-list-create')
        self.detail_url = reverse('classes:class-detail', args=[self.cls.id])

    def test_list_requires_auth(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_requires_auth(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_list_allowed_for_any_authenticated(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_filter_by_school(self):
        other_school = School.objects.create(name='مدرسه دیگر')
        make_class(other_school, self.term, subject='فیزیک')

        self.client.force_authenticate(self.edu)
        response = self.client.get(self.list_url, {'school': self.school.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data]
        self.assertIn(self.cls.id, ids)
        for item in response.data:
            self.assertEqual(item.get('school') or item.get(' school'), self.school.id)

    def test_list_filter_by_term(self):
        other_term = Term.objects.create(
            start_date='2024-07-01', end_date='2024-12-31', term_type='summer'
        )
        make_class(self.school, other_term, subject='زیست')

        self.client.force_authenticate(self.edu)
        response = self.client.get(self.list_url, {'term': self.term.id})
        ids = [item['id'] for item in response.data]
        self.assertIn(self.cls.id, ids)


    def test_create_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(self.list_url, {
            'school': self.school.id, 'term': self.term.id,
            'subject': 'شیمی', 'duration': 90,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_denied_for_finance(self):
        self.client.force_authenticate(self.finance)
        response = self.client.post(self.list_url, {
            'school': self.school.id, 'term': self.term.id,
            'subject': 'شیمی', 'duration': 90,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_education_officer(self):
        self.client.force_authenticate(self.edu)
        response = self.client.post(self.list_url, {
            'school': self.school.id, 'term': self.term.id,
            'subject': 'شیمی', 'duration': 90,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], 'شیمی')


    def test_retrieve_returns_nested_detail(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get('school'), dict)
        self.assertIsInstance(response.data.get('term'), dict)


    def test_patch_denied_for_non_edu(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.patch(self.detail_url, {'subject': 'فیزیک'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_allowed_for_edu(self):
        self.client.force_authenticate(self.edu)
        response = self.client.patch(self.detail_url, {'subject': 'فیزیک'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cls.refresh_from_db()
        self.assertEqual(self.cls.subject, 'فیزیک')


    def test_delete_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_soft_deletes(self):
        self.client.force_authenticate(self.edu)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.cls.refresh_from_db()
        self.assertTrue(self.cls.is_deleted)
        self.assertIsNotNone(self.cls.deleted_at)

    def test_soft_deleted_class_excluded_from_list(self):
        self.cls.soft_delete()
        self.client.force_authenticate(self.edu)
        response = self.client.get(self.list_url)
        ids = [item['id'] for item in response.data]
        self.assertNotIn(self.cls.id, ids)


class ClassTeacherViewsTestCase(APITestCase):
    def setUp(self):
        self.school = make_school()
        self.term = make_term()
        self.cls = make_class(self.school, self.term)

        self.edu = User.objects.create_user(
            username='edu', password='pass', role='education_officer'
        )
        self.teacher1 = User.objects.create_user(
            username='teacher1', password='pass', role='teacher',
            phone_number='+989111111111', emergency_number='+989222222222',
        )
        self.teacher2 = User.objects.create_user(
            username='teacher2', password='pass', role='teacher',
            phone_number='+989333333333', emergency_number='+989444444444',
        )

        self.list_url = reverse('classes:class-teacher-list-create')

    def _detail_url(self, pk):
        return reverse('classes:class-teacher-detail', args=[pk])

    def _post_data(self, start, end=None, teacher=None, cls=None):
        return {
            'class_obj': (cls or self.cls).id,
            'teacher': (teacher or self.teacher1).id,
            'start_date': start,
            'end_date': end,
        }

    def test_list_requires_auth(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_allowed_for_teacher(self):
        self.client.force_authenticate(self.teacher1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_assignment_edu_officer(self):
        self.client.force_authenticate(self.edu)
        response = self.client.post(self.list_url, self._post_data('2024-01-01', '2024-06-30'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_denied_for_teacher_role(self):
        self.client.force_authenticate(self.teacher1)
        response = self.client.post(self.list_url, self._post_data('2024-01-01', '2024-06-30'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_overlap_rejected(self):
        self.client.force_authenticate(self.edu)
        self.client.post(self.list_url, self._post_data('2024-01-01', '2024-06-30'))
        response = self.client.post(
            self.list_url,
            self._post_data('2024-03-01', '2024-08-31', teacher=self.teacher2),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_adjacent_no_overlap_accepted(self):
        self.client.force_authenticate(self.edu)
        self.client.post(self.list_url, self._post_data('2024-01-01', '2024-03-31'))
        response = self.client.post(
            self.list_url,
            self._post_data('2024-04-01', '2024-06-30', teacher=self.teacher2),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_open_ended_then_overlap_rejected(self):
        self.client.force_authenticate(self.edu)
        self.client.post(self.list_url, self._post_data('2024-01-01', None))
        response = self.client.post(
            self.list_url,
            self._post_data('2024-06-01', None, teacher=self.teacher2),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_assignment_edu(self):
        self.client.force_authenticate(self.edu)
        r = self.client.post(self.list_url, self._post_data('2024-01-01', '2024-06-30'))
        pk = r.data['id']

        response = self.client.patch(self._detail_url(pk), {'end_date': '2024-05-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_overlap_rejected(self):
        self.client.force_authenticate(self.edu)
        r1 = self.client.post(self.list_url, self._post_data('2024-01-01', '2024-03-31'))
        r2 = self.client.post(
            self.list_url,
            self._post_data('2024-05-01', '2024-08-31', teacher=self.teacher2),
        )
        pk1 = r1.data['id']

        response = self.client.patch(self._detail_url(pk1), {'end_date': '2024-06-01'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_assignment_soft_deletes(self):
        self.client.force_authenticate(self.edu)
        r = self.client.post(self.list_url, self._post_data('2024-01-01', '2024-06-30'))
        pk = r.data['id']

        response = self.client.delete(self._detail_url(pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        ct = ClassTeacher.all_objects.get(pk=pk)
        self.assertTrue(ct.is_deleted)
        self.assertIsNotNone(ct.deleted_at)

    def test_current_teacher_shown_in_class_detail(self):
        today = timezone.now().date()

        ClassTeacher.objects.create(
            class_obj=self.cls,
            teacher=self.teacher1,
            start_date=today,
            end_date=None,
        )

        self.client.force_authenticate(self.teacher1)
        url = reverse('classes:class-detail', args=[self.cls.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('current_teacher'))
        self.assertEqual(response.data['current_teacher']['id'], self.teacher1.id)

    def test_no_current_teacher_when_all_ended(self):
        ClassTeacher.objects.create(
            class_obj=self.cls,
            teacher=self.teacher1,
            start_date='2023-01-01',
            end_date='2023-06-30',
        )

        self.client.force_authenticate(self.teacher1)
        url = reverse('classes:class-detail', args=[self.cls.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get('current_teacher'))

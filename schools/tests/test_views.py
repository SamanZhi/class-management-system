from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from schools.models import School
from users.models import User


class SchoolViewTestCase(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher A', password='pass123', role='teacher',
            phone_number='=981234567890', emergency_number='+989876543210'
        )
        self.education_officer = User.objects.create_user(
                    username='edu_officer A', password='pass456', role='education_officer',
        )
        self.finance_officer = User.objects.create_user(
                            username='fin_officer A', password='pass789', role='finance_officer',
        )
        self.school = School.objects.create(Name='School A')
        self.list_url = reverse('schools:school-list-create')
        self.detail_url = reverse('schools:school-detail', args=[self.school.id])

    def test_list_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_allowed_for_any_authenticated_role(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(self.list_url, {'name': 'New School'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)
        response = self.client.post(self.list_url, {'name': 'New School'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_denied_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)
        response = self.client.post(self.list_url, {'name': 'New School'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_allowed_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_allowed_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.patch(self.detail_url, {'name': 'changed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_denied_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)
        response = self.client.patch(self.detail_url, {'name': 'changed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)
        response = self.client.patch(self.detail_url, {'name': 'changed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_denied_for_non_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.school.refresh_from_db()
        self.assertTrue(self.school.is_deleted)
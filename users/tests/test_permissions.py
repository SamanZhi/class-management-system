from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class PermissionTest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='saman_teacher',
            password='pass123',
            role='teacher'
        )
        self.education_officer = User.objects.create_user(
            username='saman_edu',
            password='pass456',
            role='education_officer'
        )
        self.finance_officer = User.objects.create_user(
                username='saman_fin',
                password='pass789',
                role='finance_officer'
            )

        self.teacher_url = reverse('teacher-dashboard')
        self.education_url = reverse('education-officer-dashboard')
        self.finance_url = reverse('finance-officer-dashboard')

    def test_teacher_can_access_teacher_dashboard(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.teacher_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_access_education_dashboard(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.education_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_access_finance_dashboard(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.finance_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_education_officer_can_access_education_dashboard(self):
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(self.education_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_education_officer_cannot_access_teacher_dashboard(self):
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(self.teacher_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_education_officer_cannot_access_finance_dashboard(self):
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(self.finance_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_finance_officer_can_access_finance_dashboard(self):
        self.client.force_authenticate(user=self.finance_officer)
        response = self.client.get(self.finance_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_finance_officer_cannot_access_teacher_dashboard(self):
        self.client.force_authenticate(user=self.finance_officer)
        response = self.client.get(self.teacher_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_finance_officer_cannot_access_education_dashboard(self):
        self.client.force_authenticate(user=self.finance_officer)
        response = self.client.get(self.education_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
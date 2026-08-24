from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Term
from users.models import User


class TermViewTest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='=+989123456789',
            emergency_number='+989876543210'
        )

        self.education_officer = User.objects.create_user(
            username='test_education_officer',
            password='pass456',
            role='education_officer'
        )

        self.finance_officer = User.objects.create_user(
            username='test_finance_officer',
            password='pass789',
            role='finance_officer'
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
            type='regular'
        ),

        self.list_url = reverse('term_list')
        self.detail_url= reverse('term_detail', args=[self.term.id]
        )

    def test_list_requires_authentication(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_allowed_for_teacher(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_allowed_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(self.list_url, 
            {
            'start_date': '2026-09-01', 
            'end_date': '2026-11-30',
            'type': 'regular'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.post(self.list_url, 
            {
                'start_date': '2026-09-01', 
                'end_date': '2026-11-30',
                'type': 'regular'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Term.objects.filter(
                start_date=date(2026, 9, 1), 
                end_date=date(2026, 11, 30)
            ).exists()
        )

    def test_create_denied_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)

        response = self.client.post(self.list_url, 
            {
            'start_date': '2026-09-01', 
            'end_date': '2026-11-30',
            'type': 'regular'
            }
        )

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

        response = self.client.patch(self.detail_url, {'type': 'summer'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.patch(self.detail_url, {'type': 'summer'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.term.refresh_from_db()

        self.assertEqual(self.term.type, 'summer')

    def test_update_denied_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)

        response = self.client.patch(self.detail_url, {'type': 'summer'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_denied_for_teacher(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_allowed_for_education_officer(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.term.refresh_from_db()

        self.assertTrue(self.term.is_deleted)
        self.assertIsNotNone(self.term.deleted_at)

    def test_delete_denied_for_finance_officer(self):
        self.client.force_authenticate(self.finance_officer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invalid_date_range_returns_400(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.post(
            self.list_url, 
            {
                'start_date': '2026-09-30', 
                'end_date': '2026-09-01',
                'type': 'regular'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_overlapping_term_returns_400(self):
        self.client.force_authenticate(self.education_officer)

        response = self.client.post(
            self.list_url,
            {
               'start_date': '2026-09-10', 
                'end_date': '2026-10-30',
                'type': 'regular' 
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
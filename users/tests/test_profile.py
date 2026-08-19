from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class ProfileUpdateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='saman_teacher',
            password='mypass123',
            role=User.Role.TEACHER,
            phone_number='+989361208772',
            emergency_number='+989123456789'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('profile')

    def test_user_cannot_change_username(self):
        response = self.client.patch(self.url, {'username': 'new_username'})

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, 'saman_teacher')

    def test_user_cannot_change_role(self):
        response = self.client.patch(self.url, {'role': 'finance_officer'})

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.role, User.Role.TEACHER)

    def test_teacher_cannot_clear_phone_number(self):
        response = self.client.patch(self.url, {'phone_number': ''})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_user_can_update_allowed_field(self):
        response = self.client.patch(self.url, {
            'emergency_number': '+989999999999'
        })

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.emergency_number, '+989999999999')
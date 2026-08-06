from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='saman_teacher',
            password='pass123',
            role='teacher'
        )
        self.login_url = '/api/users/login/'

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'saman_teacher',
            'password': 'pass123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': 'saman_teacher',
            'password': 'pass456'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'abcd_teacher',
            'password': 'pass123'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_request_rejected(self):
        protected_url = '/api/users/.../'
        response = self.client.get(protected_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
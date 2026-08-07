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

    # def test_teacher_can_access_own_section(self):
    #     self.client.force_authenticate(user=self.teacher)
    #     response = self.client.get('/api/teachers/.../')

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_teacher_cannot_access_education_section(self):
    #     self.client.force_authenticate(user=self.teacher)
    #     response = self.client.get('/api/education/.../')

    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
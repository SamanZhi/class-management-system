from django.test import TestCase

from users.models import User


class UserModelTest(TestCase):
    def test_create_valid_user(self):
        user = User.objects.create_user(
            username='saman_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989361208772',
            emergency_number='+989123456789'
        )

        self.assertEqual(user.username, 'saman_teacher')
        self.assertEqual(user.role, 'teacher')
        self.assertTrue(user.check_password('pass123'))
        self.assertTrue(user.is_active)
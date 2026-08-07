from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
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

    def test_invalid_role_rejected(self):
        with self.assertRaises(ValidationError):
            user = User(username='invalid_user',
                        role='instructor'
            )
            user.full_clean()

    def test_duplicate_username_rejected(self):
        User.objects.create_user(
            username='saman',
            password='pass123',
            role='teacher'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='saman',
                password='pass456',
                role='education_officer'
            )

    def test_phone_numbers_validation(self):
        user = User(
            username='saman',
            password='pass123',
            role='teacher',
            phone_number='+989361208772',
            emergency_number='+989123456789'
                    )
        user.full_clean()

        with self.assertRaises(ValidationError) as context:
            user2 = User(
                username='abcd',
                password='pass456',
                role='teacher',
                phone_number='09361208772',
                emergency_number='09123456789'
            )
            user2.full_clean()

        errors = context.exception.message_dict
        self.assertIn('phone_number', errors)
        self.assertIn('emergency_number', errors)

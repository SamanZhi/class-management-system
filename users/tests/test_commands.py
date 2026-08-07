from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from users.models import User


class CreateUserCommandTest(TestCase):

    def test_create_teacher_with_valid_phone_format(self):
        out = StringIO()
        call_command(
            'create_user', 'saman_teacher', 'pass123', 'teacher',
            '--phone', '+989361208772',
            '--emergency', '+989987654321',
            stdout=out
        )
        self.assertIn('created successfully', out.getvalue())
        user = User.objects.get(username='saman_teacher')
        self.assertEqual(user.phone_number, '+989361208772')
        self.assertEqual(user.emergency_number, '+989987654321')

    def test_create_teacher_with_invalid_phone_format_fails(self):
        out = StringIO()
        call_command(
            'create_user', 'saman_teacher', 'pass123', 'teacher',
            '--phone', '989361208772',  
            '--emergency', '+989987654321',
            stdout=out
        )
        self.assertIn('Validation error', out.getvalue())
        self.assertFalse(User.objects.filter(username='saman_teacher').exists())

    def test_create_teacher_without_phone_fails(self):
        out = StringIO()
        call_command(
            'create_user', 'saman_teacher', 'pass123', 'teacher',
            '--emergency', '+989987654321',
            stdout=out
        )
        self.assertIn('Phone and emergency numbers are required', out.getvalue())
        self.assertFalse(User.objects.filter(username='saman_teacher').exists())

    def test_create_teacher_without_emergency_fails(self):
        out = StringIO()
        call_command(
            'create_user', 'saman_teacher', 'pass123', 'teacher',
            '--phone', '+989361208772',
            stdout=out
        )
        self.assertIn('Phone and emergency numbers are required', out.getvalue())
        self.assertFalse(User.objects.filter(username='saman_teacher').exists())

    def test_create_education_officer_without_phone(self):
        out = StringIO()
        call_command(
            'create_user', 'saman_edu', 'pass456', 'education_officer',
            stdout=out
        )
        self.assertIn('created successfully', out.getvalue())
        user = User.objects.get(username='saman_edu')
        self.assertIsNone(user.phone_number)
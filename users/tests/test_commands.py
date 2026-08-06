from django.core.management import call_command
from django.test import TestCase

from users.models import User


class CommandTest(TestCase):
    def test_create_user_with_valid_role(self):
        call_command('create_user', '--role=finance_officer')

        self.assertTrue(User.objects.filter(role='finance_officer').exists())

    def test_create_user_invalid_role(self):
        with self.assertRaises(SystemExit):
            call_command('create_user', '--role=instructor')
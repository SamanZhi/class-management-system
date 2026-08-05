from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Create a user with a specific role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('password', type=str, help='Password of the user')
        parser.add_argument('role', type=str, choices=['teacher', 'education_officer', 'finance_officer'], help='Role of the user')
        parser.add_argument('--phone', type=str, required=False, help='Phone number (required for teachers)')
        parser.add_argument('--emergency', type=str, required=False, help='Emergency number (required for teachers)')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        role = options['role']
        phone = options.get('phone')
        emergency = options.get('emergency')

        if role == 'teacher' and (not phone or not emergency):
            self.stdout.write(self.style.ERROR('Phone and emergency numbers are required for teachers.'))
            return

        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            phone_number=phone,
            emergency_number=emergency
        )
        self.stdout.write(self.style.SUCCESS(f'User "{username}" with role "{role}" created successfully!'))

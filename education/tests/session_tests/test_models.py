from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from education.models import Course, School, Session, Term
from users.models import User


class SessionModelTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            address='Test Address',
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 12, 20),
            type='regular',
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )
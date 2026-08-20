from datetime import date

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Course, School, Session, Term
from users.models import User


class SessionViewTests(APITestCase):

    def setUp(self):
        self.school = School.objects.create(
            name='School A',
            address='Address A',
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
            type='regular',
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90,
        )

        self.session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456788',
            emergency_number='+989876543211',
        )

        self.education_officer = User.objects.create_user(
            username='test_education_officer',
            password='pass456',
            role='education_officer',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )


        self.finance_officer = User.objects.create_user(
            username='test_finance_officer',
            password='pass789',
            role='finance_officer',
            phone_number='+989123456787',
            emergency_number='+989876543212',
        )

        self.list_url = reverse('session-list')
        self.detail_url = reverse(
            'session-detail',
            kwargs={'pk': self.session.pk},
        )
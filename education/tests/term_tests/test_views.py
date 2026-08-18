from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Term
from users.models import User


class TermViewTest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='=+989123456789',
            emergency_number='+989876543210'
        )

        self.education_officer = User.objects.create_user(
            username='test_education_officer',
            password='pass456',
            role='education_officer'
        )

        self.finance_officer = User.objects.create_user(
            username='test_finance_officer',
            password='pass789',
            role='finance_officer'
        )

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 31),
            type='regular'
        ), 

        self.list_url = reverse('term_list')
        self.detail_url= reverse('term_detail', args=[self.term.id])
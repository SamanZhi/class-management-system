from datetime import date

from django.urls import reverse
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

    def test_teacher_can_list_sessions(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_education_officer_can_list_sessions(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


    def test_finance_officer_can_list_sessions(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_teacher_cannot_create_session(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 2,
            'date': '2026-09-06',
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_create_session(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 2,
            'date': '2026-09-06',
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Session.objects.filter(
                course_obj=self.course,
                session_number=2,
            ).exists()
        )

    def test_finance_officer_cannot_create_session(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 2,
            'date': '2026-09-06',
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_can_get_session_detail(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_education_officer_can_get_session_detail(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            self.session.id,
        )

    def test_finance_officer_can_get_session_detail(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_teacher_cannot_update_session(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-06',
        }

        response = self.client.put(
            self.detail_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_update_session(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-06',
        }

        response = self.client.put(
            self.detail_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.session.refresh_from_db()

        self.assertEqual(
            self.session.date,
            date(2026, 9, 6),
        )

    def test_finance_officer_cannot_update_session(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        data = {
            'course_obj': self.course.id,
            'session_number': 1,
            'date': '2026-09-06',
        }

        response = self.client.put(
            self.detail_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_cannot_delete_session(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_delete_session(self):
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.session.refresh_from_db()

        self.assertTrue(
            self.session.is_deleted
        )

    def test_finance_officer_cannot_delete_session(self):
        self.client.force_authenticate(
            user=self.finance_officer
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
from datetime import date

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from users.models import User


class SessionReportViewTests(APITestCase):

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

        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='+989123456789',
            emergency_number='+989876543210',
        )

        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass321',
            role='teacher',
            phone_number='+989123456788',
            emergency_number='+989876543211',
        )

        self.education_officer = User.objects.create_user(
            username='test_education_officer',
            password='pass456',
            role='education_officer',
            phone_number='+989123456787',
            emergency_number='+989876543212',
        )

        self.session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 30),
        )

        self.list_url = '/session-reports/'

    def create_report(self):
        return SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Original summary',
            present_count=15,
            absent_count=2,
        )

    def test_teacher_can_create_report(self):
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': self.session.id,
                'summary': 'Today we covered Python.',
                'present_count': 15,
                'absent_count': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            session=self.session
        )

        self.assertEqual(
            report.teacher,
            self.teacher,
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

    def test_teacher_can_only_see_own_reports(self):
        own_report = self.create_report()

        session2 = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        teacher2 = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        SessionReport.objects.create(
            session=session2,
            teacher=self.teacher2,
            summary='Other teacher report',
            present_count=10,
            absent_count=5,
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]['id'],
            own_report.id,
        )

    def test_teacher_cannot_edit_another_teachers_report(self):
        report2 = SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher2,
            summary='Other report',
            present_count=10,
            absent_count=5,
        )

        url = f'/session-reports/{report2.id}/'

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.put(
            url,
            {
                'summary': 'Hacked report',
                'present_count': 100,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_teacher_cannot_submit_future_session_report(self):
        future_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2099, 1, 1),
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': future_session.id,
                'summary': 'Future report',
                'present_count': 10,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unassigned_teacher_cannot_submit_report(self):
        self.client.force_authenticate(
            user=self.teacher2
        )

        response = self.client.post(
            self.list_url,
            {
                'session': self.session.id,
                'summary': 'Unauthorized report',
                'present_count': 10,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_teacher_cannot_review_own_report(self):
        report = self.create_report()

        url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.patch(
            url,
            {
                'status': SessionReport.Status.APPROVED,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_education_officer_can_approve_report(self):
        report = self.create_report()

        url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            url,
            {
                'status': SessionReport.Status.APPROVED,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

        self.assertEqual(
            report.reviewed_by,
            self.education_officer,
        )

    def test_education_officer_can_reject_report(self):
        report = self.create_report()

        url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            url,
            {
                'status': SessionReport.Status.REJECTED,
                'rejection_reason': 'Attendance needs correction.',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.REJECTED,
        )

        self.assertEqual(
            report.rejection_reason,
            'Attendance needs correction.',
        )

        self.assertEqual(
            report.reviewed_by,
            self.education_officer,
        )

    def test_reject_without_reason_returns_400(self):
        report = self.create_report()

        url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            url,
            {
                'status': SessionReport.Status.REJECTED,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_education_officer_cannot_change_report_content(self):
        report = self.create_report()

        original_summary = report.summary
        original_present = report.present_count
        original_absent = report.absent_count

        url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            url,
            {
                'status': SessionReport.Status.APPROVED,
                'summary': 'HACKED',
                'present_count': 999,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.summary,
            original_summary,
        )

        self.assertEqual(
            report.present_count,
            original_present,
        )

        self.assertEqual(
            report.absent_count,
            original_absent,
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

    def test_approved_report_cannot_be_edited(self):
        report = self.create_report()

        review_url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        self.client.patch(
            review_url,
            {
                'status': SessionReport.Status.APPROVED,
            },
            format='json',
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        detail_url = f'/session-reports/{report.id}/'

        response = self.client.put(
            detail_url,
            {
                'summary': 'Trying to edit approved report.',
                'present_count': 20,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rejected_report_can_be_edited_and_resubmitted(self):
        report = self.create_report()

        review_url = f'/session-reports/{report.id}/review/'

        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            review_url,
            {
                'status': SessionReport.Status.REJECTED,
                'rejection_reason': 'Please correct attendance.',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.force_authenticate(
            user=self.teacher
        )

        detail_url = f'/session-reports/{report.id}/'

        response = self.client.put(
            detail_url,
            {
                'summary': 'Corrected report.',
                'present_count': 16,
                'absent_count': 1,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.summary,
            'Corrected report.',
        )

        self.assertEqual(
            report.present_count,
            16,
        )

        self.assertEqual(
            report.absent_count,
            1,
        )

    def test_full_report_lifecycle(self):
        # 1. Teacher submits report.
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.post(
            self.list_url,
            {
                'session': self.session.id,
                'summary': 'Initial report.',
                'present_count': 15,
                'absent_count': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = SessionReport.objects.get(
            session=self.session
        )

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        # 2. Education Officer rejects report.
        self.client.force_authenticate(
            user=self.education_officer
        )

        review_url = f'/session-reports/{report.id}/review/'

        response = self.client.patch(
            review_url,
            {
                'status': SessionReport.Status.REJECTED,
                'rejection_reason': 'Please correct attendance.',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.REJECTED,
        )

        # 3. Teacher edits and resubmits.
        self.client.force_authenticate(
            user=self.teacher
        )

        detail_url = f'/session-reports/{report.id}/'

        response = self.client.put(
            detail_url,
            {
                'summary': 'Corrected report.',
                'present_count': 16,
                'absent_count': 1,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.PENDING,
        )

        self.assertEqual(
            report.summary,
            'Corrected report.',
        )

        # 4. Education Officer approves the resubmitted report.
        self.client.force_authenticate(
            user=self.education_officer
        )

        response = self.client.patch(
            review_url,
            {
                'status': SessionReport.Status.APPROVED,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        report.refresh_from_db()

        self.assertEqual(
            report.status,
            SessionReport.Status.APPROVED,
        )

        # 5. Teacher cannot edit approved report anymore.
        self.client.force_authenticate(
            user=self.teacher
        )

        response = self.client.put(
            detail_url,
            {
                'summary': 'This should fail.',
                'present_count': 100,
                'absent_count': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
from datetime import date, datetime
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Course, CourseTeacher, School, Session, SessionReport, Term
from users.models import User


class SessionReportViewTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='School A', address='Address A')
        self.term = Term.objects.create(
            start_date=date(2026, 8, 1), end_date=date(2026, 10, 31), type='regular'
        )
        self.course = Course.objects.create(
            school=self.school, term=self.term, subject='Python', duration=90
        )
        self.teacher = User.objects.create_user(
            username='test_teacher', password='pass123', role='teacher',
            phone_number='+989123456789', emergency_number='+989876543210'
        )
        self.teacher2 = User.objects.create_user(
            username='new_teacher', password='pass321', role='teacher',
            phone_number='+989123456788', emergency_number='+989876543211'
        )
        self.education_officer = User.objects.create_user(
            username='test_education_officer', password='pass456', role='education_officer',
            phone_number='+989123456787', emergency_number='+989876543212'
        )
        self.finance_officer = User.objects.create_user(
            username='test_finance_officer', password='pass789', role='finance_officer',
            phone_number='+989123456786', emergency_number='+989876543213'
        )
        self.session = Session.objects.create(
            course_obj=self.course, session_number=1, date=date(2026, 8, 5)
        )
        CourseTeacher.objects.create(
            course_obj=self.course, teacher=self.teacher,
            start_date=date(2026, 8, 1), end_date=date(2026, 10, 31)
        )
        self.list_url = reverse('session-report-list')

    def aware(self, value):
        return timezone.make_aware(datetime.fromisoformat(value), timezone.get_current_timezone())

    def create_report(self, **kwargs):
        data = {
            'session': self.session, 'teacher': self.teacher,
            'summary': 'Original summary', 'present_count': 15, 'absent_count': 2,
        }
        data.update(kwargs)
        return SessionReport.objects.create(**data)

    def test_unauthenticated_user_cannot_create_report(self):
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teacher_can_create_report(self):
        self.client.force_authenticate(user=self.teacher)
        with patch('education.models.session_report.timezone.now', return_value=self.aware('2026-08-05T10:00:00')):
            response = self.client.post(self.list_url, {
                'session': self.session.id,
                'summary': 'Today we covered Python.',
                'present_count': 15,
                'absent_count': 2,
            }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = SessionReport.objects.get(session=self.session)
        self.assertEqual(report.teacher, self.teacher)
        self.assertEqual(report.status, SessionReport.Status.PENDING)
        self.assertEqual(report.late_reference_at, self.aware('2026-08-05T10:00:00'))
        self.assertEqual(report.total_late_hours, 0)

    def test_non_teacher_cannot_create_report(self):
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.post(self.list_url, {
            'session': self.session.id, 'summary': 'Report', 'present_count': 15, 'absent_count': 2,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_only_see_own_reports(self):
        own = self.create_report()
        session2 = Session.objects.create(course_obj=self.course, session_number=2, date=date(2026, 8, 6))
        SessionReport.objects.create(
            session=session2, teacher=self.teacher2, summary='Other', present_count=10, absent_count=5
        )
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], own.id)

    def test_education_officer_can_see_all_reports(self):
        own = self.create_report()
        session2 = Session.objects.create(course_obj=self.course, session_number=2, date=date(2026, 8, 6))
        other = SessionReport.objects.create(
            session=session2, teacher=self.teacher2, summary='Other', present_count=10, absent_count=5
        )
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item['id'] for item in response.data}, {own.id, other.id})

    def test_finance_officer_cannot_list_reports(self):
        self.client.force_authenticate(user=self.finance_officer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_filters_by_course_teacher_and_date(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(self.list_url, {
            'school': self.school.id,
            'course': self.course.id,
            'teacher': self.teacher.id,
            'start_date': '2026-08-05',
            'end_date': '2026-08-05',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], report.id)

    def test_teacher_cannot_view_another_teachers_report(self):
        report = self.create_report(teacher=self.teacher2)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(reverse('session-report-detail', kwargs={'pk': report.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_edit_another_teachers_report(self):
        report = self.create_report(teacher=self.teacher2)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(
            reverse('session-report-detail', kwargs={'pk': report.pk}),
            {'summary': 'Hacked', 'present_count': 100, 'absent_count': 0}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_education_officer_can_get_report_detail(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.get(reverse('session-report-detail', kwargs={'pk': report.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], report.id)

    def test_finance_officer_cannot_get_report_detail(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.finance_officer)
        response = self.client.get(reverse('session-report-detail', kwargs={'pk': report.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_edit_pending_report(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(
            reverse('session-report-detail', kwargs={'pk': report.pk}),
            {'summary': 'Updated summary', 'present_count': 16, 'absent_count': 1}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.summary, 'Updated summary')
        self.assertEqual(report.present_count, 16)
        self.assertEqual(report.status, SessionReport.Status.PENDING)

    def test_teacher_cannot_edit_approved_report(self):
        report = self.create_report(status=SessionReport.Status.APPROVED)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(
            reverse('session-report-detail', kwargs={'pk': report.pk}),
            {'summary': 'Changed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_future_session_report_is_rejected(self):
        future = Session.objects.create(course_obj=self.course, session_number=2, date=date(2099, 1, 1))
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.list_url, {
            'session': future.id, 'summary': 'Future', 'present_count': 10, 'absent_count': 0,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unassigned_teacher_cannot_submit_report(self):
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.post(self.list_url, {
            'session': self.session.id, 'summary': 'Unauthorized', 'present_count': 10, 'absent_count': 0,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_cannot_review_own_report(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(
            reverse('session-report-review', kwargs={'pk': report.pk}),
            {'status': SessionReport.Status.APPROVED}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_education_officer_can_approve_report(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.patch(
            reverse('session-report-review', kwargs={'pk': report.pk}),
            {'status': SessionReport.Status.APPROVED}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, SessionReport.Status.APPROVED)
        self.assertEqual(report.reviewed_by, self.education_officer)

    def test_education_officer_can_reject_report_and_start_new_late_cycle(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        rejected_at = self.aware('2026-08-07T10:00:00')
        with patch('education.models.session_report.timezone.now', return_value=rejected_at):
            response = self.client.patch(
                reverse('session-report-review', kwargs={'pk': report.pk}),
                {'status': SessionReport.Status.REJECTED, 'rejection_reason': 'Fix attendance.'},
                format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, SessionReport.Status.REJECTED)
        self.assertEqual(report.reviewed_by, self.education_officer)
        self.assertEqual(report.late_reference_at, rejected_at)

    def test_reject_without_reason_returns_400(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.patch(
            reverse('session-report-review', kwargs={'pk': report.pk}),
            {'status': SessionReport.Status.REJECTED}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejected_report_can_be_edited_and_resubmitted(self):
        report = self.create_report(status=SessionReport.Status.REJECTED, rejection_reason='Fix it.')
        rejection_time = self.aware('2026-08-07T10:00:00')
        report.late_reference_at = rejection_time
        report.save(update_fields=['late_reference_at'])
        self.client.force_authenticate(user=self.teacher)
        edit_time = self.aware('2026-08-09T11:20:00')
        with patch('education.models.session_report.timezone.now', return_value=edit_time):
            response = self.client.put(
                reverse('session-report-detail', kwargs={'pk': report.pk}),
                {'summary': 'Corrected', 'present_count': 16, 'absent_count': 1}, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.status, SessionReport.Status.PENDING)
        self.assertEqual(report.rejection_reason, '')
        self.assertIsNone(report.reviewed_by)
        self.assertEqual(report.total_late_hours, 2)
        self.assertEqual(report.teacher_edited_at, edit_time)
        self.assertEqual(report.late_reference_at, edit_time)

    def test_multiple_reject_edit_cycles_accumulate_late_hours(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        first_rejection = self.aware('2026-08-07T10:00:00')
        with patch('education.models.session_report.timezone.now', return_value=first_rejection):
            self.client.patch(
                reverse('session-report-review', kwargs={'pk': report.pk}),
                {'status': SessionReport.Status.REJECTED, 'rejection_reason': 'Fix one.'}, format='json'
            )

        self.client.force_authenticate(user=self.teacher)
        first_edit = self.aware('2026-08-09T11:20:00')
        with patch('education.models.session_report.timezone.now', return_value=first_edit):
            response = self.client.put(
                reverse('session-report-detail', kwargs={'pk': report.pk}),
                {'summary': 'First correction'}, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.education_officer)
        second_rejection = self.aware('2026-08-10T20:00:00')
        with patch('education.models.session_report.timezone.now', return_value=second_rejection):
            response = self.client.patch(
                reverse('session-report-review', kwargs={'pk': report.pk}),
                {'status': SessionReport.Status.REJECTED, 'rejection_reason': 'Fix two.'}, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.teacher)
        second_edit = self.aware('2026-08-12T21:00:00')
        with patch('education.models.session_report.timezone.now', return_value=second_edit):
            response = self.client.put(
                reverse('session-report-detail', kwargs={'pk': report.pk}),
                {'summary': 'Final correction'}, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        self.assertEqual(report.total_late_hours, 3)
        self.assertEqual(report.status, SessionReport.Status.PENDING)
        self.assertEqual(report.late_reference_at, second_edit)

    def test_approved_report_cannot_be_reviewed_again(self):
        report = self.create_report(status=SessionReport.Status.APPROVED)
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.patch(
            reverse('session-report-review', kwargs={'pk': report.pk}),
            {'status': SessionReport.Status.REJECTED, 'rejection_reason': 'Fix it.'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_education_officer_cannot_change_report_content(self):
        report = self.create_report()
        self.client.force_authenticate(user=self.education_officer)
        response = self.client.patch(
            reverse('session-report-review', kwargs={'pk': report.pk}),
            {'status': SessionReport.Status.APPROVED, 'summary': 'Hacked', 'present_count': 999}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report.refresh_from_db()
        self.assertEqual(report.summary, 'Original summary')
        self.assertEqual(report.present_count, 15)
        self.assertEqual(report.status, SessionReport.Status.APPROVED)

    def test_full_report_lifecycle(self):
        self.client.force_authenticate(user=self.teacher)
        create_time = self.aware('2026-08-05T10:00:00')
        with patch('education.models.session_report.timezone.now', return_value=create_time):
            response = self.client.post(self.list_url, {
                'session': self.session.id, 'summary': 'Initial', 'present_count': 15, 'absent_count': 2,
            }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = SessionReport.objects.get(session=self.session)
        self.assertEqual(report.status, SessionReport.Status.PENDING)

        self.client.force_authenticate(user=self.education_officer)
        approve_url = reverse('session-report-review', kwargs={'pk': report.pk})
        response = self.client.patch(approve_url, {'status': SessionReport.Status.APPROVED}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        self.assertEqual(report.status, SessionReport.Status.APPROVED)

        self.client.force_authenticate(user=self.teacher)
        response = self.client.put(
            reverse('session-report-detail', kwargs={'pk': report.pk}),
            {'summary': 'Should fail'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

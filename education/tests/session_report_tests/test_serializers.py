from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from education.models import (
    Course,
    CourseTeacher,
    School,
    Session,
    SessionReport,
    Term,
)
from education.serializers.session_report import (
    SessionReportReviewSerializer,
    SessionReportSerializer,
)
from users.models import User


class SessionReportSerializerTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        
        self.school = School.objects.create(
            name='School A',
            address='Address A',
        )

        session_date = timezone.localdate() - timedelta(days=1)

        self.term = Term.objects.create(
            start_date=session_date - timedelta(days=30),
            end_date=session_date + timedelta(days=60),
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

        self.other_teacher = User.objects.create_user(
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
            date=session_date,
        )

        CourseTeacher.objects.create(
            course_obj=self.course,
            teacher=self.teacher,
            start_date=session_date - timedelta(days=10),
            end_date=session_date + timedelta(days=30),
        )

    def get_context(self, user):
        request = self.factory.post('/api/education/session-reports/')
        request.user = user

        return {'request': request}

    def valid_data(self):
        return {
            'session': self.session.id,
            'summary': 'Students completed the lesson.',
            'present_count': 15,
            'absent_count': 2,
        }

    def test_valid_report_data(self):
        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_future_session_is_invalid(self):
        future_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2099, 1, 1),
        )

        data = self.valid_data()
        data['session'] = future_session.id

        serializer = SessionReportSerializer(
            data=data,
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)

    def test_teacher_must_be_responsible_on_session_date(self):
        CourseTeacher.objects.filter(
            course_obj=self.course,
            teacher=self.teacher,
        ).delete()

        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)

    def test_teacher_before_start_date_is_invalid(self):
        CourseTeacher.objects.filter(
            course_obj=self.course,
            teacher=self.teacher,
        ).update(
            start_date=date(2026, 9, 10),
        )

        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())

    def test_teacher_after_end_date_is_invalid(self):
        CourseTeacher.objects.filter(
            course_obj=self.course,
            teacher=self.teacher,
        ).update(
            end_date=date(2026, 8, 19),
        )

        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())

    def test_teacher_with_no_end_date_is_valid(self):
        CourseTeacher.objects.filter(
            course_obj=self.course,
            teacher=self.teacher,
        ).update(
            end_date=None,
        )

        serializer = SessionReportSerializer(
            data=self.valid_data(),
            context=self.get_context(self.teacher),
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_approved_report_cannot_be_updated(self):
        report = SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Original summary',
            present_count=15,
            absent_count=2,
            status=SessionReport.Status.APPROVED,
        )

        serializer = SessionReportSerializer(
            report,
            data={
                'summary': 'Changed summary',
                'present_count': 20,
                'absent_count': 0,
            },
            partial=True,
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())

    def test_session_cannot_be_changed_on_update(self):
        second_session = Session.objects.create(
            course_obj=self.course,
            session_number=2,
            date=date(2026, 9, 6),
        )

        report = SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Original summary',
            present_count=15,
            absent_count=2,
        )

        serializer = SessionReportSerializer(
            report,
            data={
                'session': second_session.id,
                'summary': 'Updated summary',
            },
            partial=True,
            context=self.get_context(self.teacher),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('session', serializer.errors)

    def test_teacher_is_read_only(self):
        serializer = SessionReportSerializer()

        self.assertIn(
            'teacher',
            serializer.fields,
        )
        self.assertTrue(
            serializer.fields['teacher'].read_only
        )

    def test_status_is_read_only(self):
        serializer = SessionReportSerializer()

        self.assertTrue(
            serializer.fields['status'].read_only
        )

    def test_rejection_reason_is_read_only_for_teacher(self):
        serializer = SessionReportSerializer()

        self.assertTrue(
            serializer.fields['rejection_reason'].read_only
        )


class SessionReportReviewSerializerTests(TestCase):

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

        self.session = Session.objects.create(
            course_obj=self.course,
            session_number=1,
            date=date(2026, 9, 5),
        )

        self.report = SessionReport.objects.create(
            session=self.session,
            teacher=self.teacher,
            summary='Test report',
            present_count=15,
            absent_count=2,
        )

    def test_approve_is_valid(self):
        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.APPROVED,
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_reject_with_reason_is_valid(self):
        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.REJECTED,
                'rejection_reason': 'Attendance count is incorrect.',
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_reject_without_reason_is_invalid(self):
        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.REJECTED,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'rejection_reason',
            serializer.errors,
        )

    def test_pending_status_cannot_be_used_for_review(self):
        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.PENDING,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_approved_report_cannot_be_reviewed_again(self):
        self.report.status = SessionReport.Status.APPROVED
        self.report.save()

        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.REJECTED,
                'rejection_reason': 'Invalid.',
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())

    def test_rejected_report_cannot_be_reviewed_again(self):
        self.report.status = SessionReport.Status.REJECTED
        self.report.rejection_reason = 'Needs correction.'
        self.report.save()

        serializer = SessionReportReviewSerializer(
            self.report,
            data={
                'status': SessionReport.Status.APPROVED,
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
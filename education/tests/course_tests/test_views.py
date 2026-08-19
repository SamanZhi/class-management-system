from datetime import date

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from education.models import Course, CourseTeacher, School, Term

from users.models import User


class CourseViewTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='School A', address='Address A')

        self.term = Term.objects.create(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 11, 31),
            type='regular'
        )

        
        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='pass123',
            role='teacher',
            phone_number='=+989123456789',
            emergency_number='+989876543210'
        )

        
        self.teacher2 = User.objects.create_user(
            username='new_teacher',
            password='pass456',
            role='teacher',
            phone_number='=+981234567890',
            emergency_number='+989123456789'
        )

        self.education_officer = User.objects.create_user(
            username='edu_officer A', password='pass456', role='education_officer',
        )

        self.finance_officer = User.objects.create_user(
            username='fin_officer A', password='pass789', role='finance_officer',
        )

        self.course = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Python',
            duration=90
        )

        self.teacher_assignment = CourseTeacher.objects.create(
            course_obj= self.course,
            teacher=self.teacher,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 10, 30)
        )

        self.course2 = Course.objects.create(
            school=self.school,
            term=self.term,
            subject='Django',
            duration=120
        )

        CourseTeacher.objects.create(
            course_obj= self.course2,
            teacher=self.teacher2,
            start_date=date(2026, 9, 15),
            end_date=date(2026, 11, 10)
        )

        self.list_url = reverse('course-list')
        self.detail_url = reverse(
            'course-detail', 
            args=[self.course.id]
        )
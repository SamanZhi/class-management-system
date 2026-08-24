import math
from datetime import datetime, time
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from education.models import SessionReport

from .models import PayrollRecord, TeacherTermRate

PERCENT_60 = Decimal('0.7')
PERCENT_120 = Decimal('1.3')
SUMMER_MULTIPLIER = Decimal('1.1')
LATE_PENALTY_PER_HOUR = Decimal('0.01')
MAX_LATE_PENALTY = Decimal('1.0')


def get_session_datetime(session):
    session_datetime = datetime.combine(
        session.date,
        time.min
    )

    if timezone.is_naive(session_datetime):
        session_datetime = timezone.make_aware(
            session_datetime,
            timezone.get_current_timezone(),
        )

    return session_datetime


def get_late_penalty(report):
    """
    Returns the penalty percentage for a late report.

    Example:
        1 hour late   -> 1%
        1:20 late     -> 2%
        5 hours late  -> 5%
        120 hours     -> 100% (maximum)
    """

    if not report.is_late:
        return Decimal(0)

    session_datetime = get_session_datetime(report.session)
    updated_at = report.updated_at

    if timezone.is_naive(updated_at):
        updated_at = timezone.make_aware(
            updated_at,
            timezone.get_current_timezone(),
        )

    delay = updated_at - session_datetime
    delay_seconds = delay.total_seconds()
    delay_hours = math.ceil(delay_seconds / 3600)
    penalty = Decimal(delay_hours) * LATE_PENALTY_PER_HOUR

    return min(penalty, MAX_LATE_PENALTY)


def get_session_base_wage(report, base_rate):
    """
    Calculates the gross wage of one session before late penalty.
    """

    duration = report.session.course_obj.duration

    if duration == 60:
        return base_rate * PERCENT_60

    if duration == 90:
        return base_rate
    
    if duration == 120:
        return base_rate * PERCENT_120

    raise ValueError(
        f"Unsupported session duration {duration}"
    )

@transaction.atomic
def calculate_teacher_payroll(teacher, year, month):
    """
    Calculate and store payroll for one teacher in one month.

    Only APPROVED reports are considered.
    Late reports are included and receive a 1% penalty per
    rounded-up hour of delay.
    """

    reports = (
        SessionReport.objects
        .filter(
            teacher=teacher,
            status=SessionReport.status.APPROVED,
            session__date__year=year,
            session__date__month=month,
        )
        .select_related(
            'session',
            'session__course_obj',
            'session__course_obj__term',
        )
    )

    valid_reports = list(reports)

    if not valid_reports:
        return

    term = valid_reports[0].session.course_obj.term

    rate = TeacherTermRate.objects.get(
        teacher=teacher,
        term=term,
    )

    base_rate = rate.base_rate

    session_60 = 0
    session_90 = 0
    session_120 = 0

    wage = Decimal(0)

    for report in valid_reports:
        duration = report.session.course_obj.duration

        if duration == 60:
            session_60 +=1
        elif duration == 90:
            session_90 += 1
        elif duration == 120:
            session_120 += 1
        else:
            raise ValueError(
                f"unsupported session duration: {duration}"
            )

        session_wage = get_session_base_wage(
            report,
            base_rate,
        )

        penalty = get_late_penalty(report)

        session_wage *= (Decimal(1) - penalty)

        wage += session_wage

    if term.type == 'summer':
        wage *= SUMMER_MULTIPLIER

    payroll, _ = PayrollRecord.objects.update_or_create(
        teacher=teacher,
        year=year,
        month=month,
        defaults={
            'amount': wage,
            'session_60': session_60,
            'session_90': session_90,
            'session_120': session_120
        }
    )

    return payroll
    
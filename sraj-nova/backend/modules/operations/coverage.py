from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from modules.operations.models import ShiftAssignment
from modules.workforce.models import Employee, EmployeeStatus


def shift_bounds(shift):
    zone = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(shift.work_date, shift.starts_at), zone)
    end = timezone.make_aware(datetime.combine(shift.work_date, shift.ends_at), zone)
    if end <= start:
        end += timedelta(days=1)
    return start, end


def assignment_block(employee, shift) -> str | None:
    required = shift.position.required_skill
    if required and not employee.qualifications.filter(skill=required).exists():
        return f"Missing required skill: {required}."
    if employee.status != EmployeeStatus.ACTIVE:
        return "Worker is not active."
    start, end = shift_bounds(shift)
    others = ShiftAssignment.objects.filter(
        employee=employee,
        work_date__gte=shift.work_date - timedelta(days=2),
        work_date__lte=shift.work_date + timedelta(days=2),
    ).exclude(pk=shift.pk)
    minimum = timedelta(hours=settings.MIN_REST_HOURS)
    for other in others:
        other_start, other_end = shift_bounds(other)
        if other_start < end and start < other_end:
            return "Already assigned to an overlapping shift."
        if timedelta(0) <= start - other_end < minimum or timedelta(0) <= other_start - end < minimum:
            return f"Fewer than {settings.MIN_REST_HOURS} hours between shifts."
    return None


def coverage(day=None) -> list[dict]:
    day = day or timezone.localdate()
    open_shifts = (
        ShiftAssignment.objects.filter(work_date=day, employee__isnull=True)
        .select_related("client", "position", "site")
        .order_by("starts_at")
    )
    workers = list(Employee.objects.filter(status=EmployeeStatus.ACTIVE).prefetch_related("qualifications"))
    rows = []
    for shift in open_shifts:
        recommendations = []
        blocked = []
        for worker in workers:
            reason = assignment_block(worker, shift)
            item = {
                "employee_id": str(worker.id),
                "employee_number": worker.agency_employee_number,
                "name": f"{worker.first_name} {worker.last_name}",
            }
            if reason is None:
                recommendations.append({**item, "reason": "Skill matches and the rest interval is satisfied."})
            elif shift.position.required_skill and worker.qualifications.filter(skill=shift.position.required_skill).exists():
                blocked.append({**item, "reason": reason})
        rows.append(
            {
                "shift_id": str(shift.id),
                "client_name": shift.client.legal_name,
                "site_name": shift.site.name,
                "position": shift.position.title,
                "required_skill": shift.position.required_skill,
                "starts_at": shift.starts_at.isoformat(timespec="minutes"),
                "ends_at": shift.ends_at.isoformat(timespec="minutes"),
                "recommendations": recommendations,
                "blocked": blocked,
            }
        )
    return rows

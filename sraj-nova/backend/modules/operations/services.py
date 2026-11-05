from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from modules.identity.models import AGENCY_ROLES, AgencyRole
from modules.operations.models import AttendanceEvent, OperationalAlert, ShiftAssignment, StaffingRequest
from modules.organization.models import Client, ServiceContract
from modules.workforce.models import Deployment, Employee, EmployeeStatus


def scoped_clients(user):
    if user.role in AGENCY_ROLES:
        return Client.objects.all()
    if user.role == AgencyRole.CLIENT_USER and user.client_id:
        return Client.objects.filter(pk=user.client_id)
    return Client.objects.none()


def scoped_employees(user):
    if user.role in AGENCY_ROLES:
        return Employee.objects.all()
    if user.role == AgencyRole.CLIENT_USER and user.client_id:
        return Employee.objects.filter(deployments__client_id=user.client_id, deployments__is_current=True).distinct()
    if user.role == AgencyRole.EMPLOYEE and user.employee_id:
        return Employee.objects.filter(pk=user.employee_id)
    return Employee.objects.none()


def _attendance_state(employee_id, work_date, starts_at) -> str:
    events = list(
        AttendanceEvent.objects.filter(employee_id=employee_id, occurred_at__date=work_date).order_by("occurred_at")
    )
    first_in = next((event for event in events if event.event_type == "in"), None)
    if first_in is None:
        return "absent"
    start = timezone.make_aware(datetime.combine(work_date, starts_at), timezone.get_current_timezone())
    if timezone.localtime(first_in.occurred_at) > start + timedelta(minutes=settings.LATE_GRACE_MINUTES):
        return "late"
    if events[-1].event_type == "in":
        return "on_duty"
    return "present"


def command_center(user) -> dict:
    clients = scoped_clients(user)
    today = timezone.localdate()
    deployments = Deployment.objects.filter(is_current=True, client__in=clients)
    shifts = ShiftAssignment.objects.filter(work_date=today, client__in=clients)
    scheduled = shifts.exclude(employee__isnull=True)
    states = [_attendance_state(shift.employee_id, today, shift.starts_at) for shift in scheduled]
    per_client = list(
        deployments.values("client_id", "client__legal_name").annotate(workers=Count("id")).order_by("client__legal_name")
    )
    horizon = today + timedelta(days=30)
    return {
        "as_of": today.isoformat(),
        "scope": "agency" if user.role in AGENCY_ROLES else "client",
        "active_workforce": Employee.objects.filter(status=EmployeeStatus.ACTIVE, id__in=deployments.values("employee_id")).count()
        if user.role not in AGENCY_ROLES
        else Employee.objects.filter(status=EmployeeStatus.ACTIVE).count(),
        "deployed_workers": deployments.count(),
        "workers_by_client": [
            {"client_id": str(row["client_id"]), "client_name": row["client__legal_name"], "workers": row["workers"]}
            for row in per_client
        ],
        "scheduled_today": scheduled.count(),
        "on_duty": states.count("on_duty"),
        "late": states.count("late"),
        "absent": states.count("absent"),
        "unfilled_shifts": shifts.filter(employee__isnull=True).count(),
        "pending_staffing_requests": StaffingRequest.objects.filter(status="pending", client__in=clients).count(),
        "expiring_contracts": ServiceContract.objects.filter(client__in=clients, ends_on__gte=today, ends_on__lte=horizon).count(),
        "open_alerts": [
            {"severity": alert.severity, "message": alert.message}
            for alert in OperationalAlert.objects.filter(is_open=True, client__in=clients).order_by("-created_at")[:8]
        ],
        "finance": _finance_block(user),
    }


def _finance_block(user) -> dict:
    from modules.finance.services import finance_summary

    summary = finance_summary(user)
    block = {
        "payroll_engine": "scheduled_hours_x_rate",
        "billing_engine": "cost_plus_fee",
        "statutory_engine": "not_active",
        "weekly_gross_payroll": summary["weekly_gross_payroll"],
        "estimated_net_payroll": None,
        "statutory_liabilities": None,
        "outstanding_invoices": summary["outstanding_invoices"],
        "agency_fee_revenue": summary["agency_fee"],
        "reason": summary["basis"],
    }
    if "cash_available" in summary:
        block["cash_available"] = summary["cash_available"]
    return block

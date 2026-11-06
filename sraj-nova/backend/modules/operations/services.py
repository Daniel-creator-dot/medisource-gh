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
        "board": _executive_board(user, clients, today),
    }


def _executive_board(user, clients, today) -> dict:
    """Series for the command center. Every amount is a stored invoice, shift, or journal."""
    from decimal import Decimal

    from modules.finance.ledger import invoice_outstanding
    from modules.finance.models import ClientInvoice, ClientReceipt, JournalEntry
    from modules.finance.services import money, money_str

    start = today - timedelta(days=today.weekday())
    days = [start + timedelta(days=offset) for offset in range(7)]
    week_shifts = list(
        ShiftAssignment.objects.filter(work_date__gte=start, work_date__lte=days[-1], client__in=clients).select_related(
            "client", "site"
        )
    )
    attendance_week = []
    for day in days:
        day_shifts = [shift for shift in week_shifts if shift.work_date == day]
        filled = [shift for shift in day_shifts if shift.employee_id]
        future = day > today
        states = [] if future else [_attendance_state(shift.employee_id, day, shift.starts_at) for shift in filled]
        attendance_week.append(
            {
                "date": day.isoformat(),
                "is_today": day == today,
                "future": future,
                "scheduled": len(filled),
                "unfilled": len(day_shifts) - len(filled),
                "on_duty": None if future else states.count("on_duty"),
                "present": None if future else states.count("present"),
                "late": None if future else states.count("late"),
                "absent": None if future else states.count("absent"),
            }
        )
    heatmap = {}
    for shift in week_shifts:
        label = f"{shift.client.legal_name} · {shift.site.name}"
        cells = heatmap.setdefault(label, {day.isoformat(): {"filled": 0, "unfilled": 0} for day in days})
        bucket = "filled" if shift.employee_id else "unfilled"
        cells[shift.work_date.isoformat()][bucket] += 1
    invoices = list(ClientInvoice.objects.filter(client__in=clients).select_related("client").order_by("week_start", "client__legal_name"))
    weeks = {}
    current_clients = []
    unpaid = []
    for invoice in invoices:
        outstanding = invoice_outstanding(invoice)
        week = weeks.setdefault(
            invoice.week_start.isoformat(),
            {"week_start": invoice.week_start.isoformat(), "employment_cost": Decimal("0.00"), "agency_fee": Decimal("0.00"), "outstanding": Decimal("0.00")},
        )
        week["employment_cost"] = money(week["employment_cost"] + invoice.employment_cost)
        week["agency_fee"] = money(week["agency_fee"] + invoice.agency_fee)
        week["outstanding"] = money(week["outstanding"] + outstanding)
        if invoice.week_start == start:
            current_clients.append(
                {
                    "client_name": invoice.client.legal_name,
                    "employment_cost": money_str(invoice.employment_cost),
                    "agency_fee": money_str(invoice.agency_fee),
                    "outstanding": money_str(outstanding),
                }
            )
        if outstanding > 0:
            unpaid.append(
                {
                    "client_name": invoice.client.legal_name,
                    "week_start": invoice.week_start.isoformat(),
                    "outstanding": money_str(outstanding),
                }
            )
    activity = []
    for event in AttendanceEvent.objects.filter(employee__in=scoped_employees(user)).select_related("employee").order_by("-created_at")[:8]:
        activity.append(
            {
                "at": event.created_at.isoformat(),
                "kind": "attendance",
                "text": f"{event.employee.agency_employee_number} {event.event_type} punch stored",
                "href": "/floor",
            }
        )
    for request in StaffingRequest.objects.filter(client__in=clients).order_by("-created_at")[:8]:
        activity.append(
            {
                "at": request.created_at.isoformat(),
                "kind": "staffing",
                "text": f"{request.title} · {request.headcount} · {request.status}",
                "href": "/work",
            }
        )
    journal_query = JournalEntry.objects.all() if user.role in AGENCY_ROLES else JournalEntry.objects.filter(invoice__client__in=clients)
    for entry in journal_query.order_by("-created_at")[:8]:
        activity.append({"at": entry.created_at.isoformat(), "kind": "journal", "text": entry.memo, "href": "/accounting"})
    for receipt in ClientReceipt.objects.filter(client__in=clients).order_by("-created_at")[:8]:
        activity.append(
            {
                "at": receipt.created_at.isoformat(),
                "kind": "receipt",
                "text": f"Receipt {receipt.reference} · GHS {money_str(receipt.amount)}",
                "href": "/accounting",
            }
        )
    activity.sort(key=lambda item: item["at"], reverse=True)
    return {
        "attendance_week": attendance_week,
        "heatmap": [{"site": name, "days": [{"date": day, **cells[day]} for day in cells]} for name, cells in sorted(heatmap.items())],
        "invoice_weeks": [
            {
                "week_start": row["week_start"],
                "employment_cost": money_str(row["employment_cost"]),
                "agency_fee": money_str(row["agency_fee"]),
                "outstanding": money_str(row["outstanding"]),
            }
            for row in weeks.values()
        ],
        "clients_this_week": current_clients,
        "unpaid_invoices": unpaid,
        "activity": activity[:8],
        "payroll_approvals": [],
        "payroll_approval_note": "No payroll run is stored, so nothing is waiting for approval.",
        "net_profitability": None,
        "net_profitability_reason": "Fee revenue is not profit. Wage expense, PAYE, and pension are not posted.",
        "statutory_note": "No statutory obligation is stored.",
    }


def factory_floor(user) -> dict:
    """Today's factory shifts, skill cover, leave, and certification dates from stored records."""
    from modules.finance.services import money_str, shift_hours
    from modules.workforce.models import Certification, LeaveRequest, PayProfile, Qualification

    clients = scoped_clients(user)
    employees = scoped_employees(user)
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    agency = user.role in AGENCY_ROLES
    shifts = (
        ShiftAssignment.objects.filter(work_date__gte=start, work_date__lte=end, client__in=clients)
        .select_related("client", "site", "department", "position", "employee")
        .order_by("work_date", "site__name", "starts_at")
    )
    qualified = set(Qualification.objects.filter(employee__in=employees).values_list("employee_id", "skill"))
    rows = []
    for shift in shifts:
        skill = shift.position.required_skill
        if shift.employee_id is None:
            cover = "open" if skill else "not_required"
            attendance = "unfilled"
        elif shift.work_date > today:
            if not skill:
                cover = "not_required"
            elif (shift.employee_id, skill) in qualified:
                cover = "covered"
            else:
                cover = "gap"
            attendance = "scheduled"
        elif not skill:
            cover = "not_required"
            attendance = _attendance_state(shift.employee_id, today if shift.work_date == today else shift.work_date, shift.starts_at)
        elif (shift.employee_id, skill) in qualified:
            cover = "covered"
            attendance = _attendance_state(shift.employee_id, shift.work_date, shift.starts_at)
        else:
            cover = "gap"
            attendance = _attendance_state(shift.employee_id, shift.work_date, shift.starts_at)
        row = {
            "id": str(shift.id),
            "work_date": shift.work_date.isoformat(),
            "is_today": shift.work_date == today,
            "client_name": shift.client.legal_name,
            "site_name": shift.site.name,
            "city": shift.site.city,
            "department": shift.department.name,
            "position": shift.position.title,
            "required_skill": skill,
            "skill_cover": cover,
            "starts_at": shift.starts_at.strftime("%H:%M"),
            "ends_at": shift.ends_at.strftime("%H:%M"),
            "hours": money_str(shift_hours(shift)),
            "attendance": attendance,
            "employee_id": str(shift.employee_id) if shift.employee_id else None,
            "worker_number": shift.employee.agency_employee_number if shift.employee_id else None,
            "worker_name": f"{shift.employee.first_name} {shift.employee.last_name}" if shift.employee_id else None,
        }
        if agency and shift.employee_id:
            try:
                rate = shift.employee.pay_profile.hourly_rate
            except PayProfile.DoesNotExist:
                rate = None
            if rate is not None:
                row["hourly_rate"] = money_str(rate)
                row["labor_cost"] = money_str(shift_hours(shift) * rate)
        rows.append(row)
    horizon = today + timedelta(days=60)
    certifications = [
        {
            "employee_id": str(item.employee_id),
            "worker_name": f"{item.employee.first_name} {item.employee.last_name}",
            "name": item.name,
            "expires_on": item.expires_on.isoformat(),
            "state": "expired" if item.expires_on < today else "due",
        }
        for item in Certification.objects.filter(employee__in=employees, expires_on__isnull=False, expires_on__lte=horizon)
        .select_related("employee")
        .order_by("expires_on")
    ]
    leave = [
        {
            "employee_id": str(item.employee_id),
            "worker_name": f"{item.employee.first_name} {item.employee.last_name}",
            "starts_on": item.starts_on.isoformat(),
            "ends_on": item.ends_on.isoformat(),
            "status": item.status,
        }
        for item in LeaveRequest.objects.filter(
            employee__in=employees, status="approved", starts_on__lte=today, ends_on__gte=today
        ).select_related("employee")
    ]
    return {"as_of": today.isoformat(), "week_start": start.isoformat(), "shifts": rows, "certifications": certifications, "leave": leave}


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

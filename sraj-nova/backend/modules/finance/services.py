from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from modules.finance.models import CashMovement, ClientInvoice
from modules.identity.models import AGENCY_ROLES
from modules.operations.models import ShiftAssignment
from modules.operations.services import scoped_clients
from modules.organization.models import ServiceContract
from modules.workforce.models import PayProfile

TWOPLACES = Decimal("0.01")
BASIS = (
    "Gross wages are scheduled shift hours multiplied by each worker's stored hourly rate. "
    "The agency fee is the contract management-fee rate applied to that cost. "
    "PAYE, pension, and net pay are not calculated."
)


def money(value) -> Decimal:
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def money_str(value) -> str:
    return format(money(value), "f")


def shift_hours(shift) -> Decimal:
    start = datetime.combine(shift.work_date, shift.starts_at)
    end = datetime.combine(shift.work_date, shift.ends_at)
    if end <= start:
        end += timedelta(days=1)
    return (Decimal((end - start).total_seconds()) / Decimal(3600)).quantize(Decimal("0.01"))


def week_start(day=None):
    day = day or timezone.localdate()
    return day - timedelta(days=day.weekday())


def rebuild_week_invoices(day=None) -> None:
    start = week_start(day)
    end = start + timedelta(days=6)
    ClientInvoice.objects.filter(week_start=start, is_demo=True).delete()
    costs: dict = {}
    shifts = ShiftAssignment.objects.filter(
        work_date__gte=start, work_date__lte=end, employee__isnull=False
    ).select_related("employee__pay_profile", "client")
    for shift in shifts:
        try:
            profile = shift.employee.pay_profile
        except PayProfile.DoesNotExist:
            continue
        costs[shift.client_id] = costs.get(shift.client_id, Decimal("0.00")) + money(shift_hours(shift) * profile.hourly_rate)
    for client_id, cost in costs.items():
        contract = ServiceContract.objects.filter(client_id=client_id).order_by("-ends_on").first()
        rate = contract.management_fee_rate if contract is not None else Decimal("0")
        ClientInvoice.objects.update_or_create(
            client_id=client_id,
            week_start=start,
            defaults={
                "employment_cost": money(cost),
                "agency_fee": money(cost * rate),
                "currency": "GHS",
                "status": "issued",
                "is_demo": True,
            },
        )


def finance_summary(user) -> dict:
    clients = scoped_clients(user)
    start = week_start()
    invoices = list(ClientInvoice.objects.filter(week_start=start, client__in=clients).select_related("client"))
    employment = sum((invoice.employment_cost for invoice in invoices), Decimal("0.00"))
    fee = sum((invoice.agency_fee for invoice in invoices), Decimal("0.00"))
    payload = {
        "week_start": start.isoformat(),
        "currency": "GHS",
        "weekly_gross_payroll": money_str(employment),
        "agency_fee": money_str(fee),
        "outstanding_invoices": money_str(employment + fee),
        "estimated_net_payroll": None,
        "statutory_liabilities": None,
        "basis": BASIS,
        "invoices": [
            {
                "client_name": invoice.client.legal_name,
                "employment_cost": money_str(invoice.employment_cost),
                "agency_fee": money_str(invoice.agency_fee),
                "total": money_str(invoice.employment_cost + invoice.agency_fee),
                "status": invoice.status,
                "is_demo": invoice.is_demo,
            }
            for invoice in invoices
        ],
    }
    if user.role in AGENCY_ROLES:
        cash = CashMovement.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        payload["cash_available"] = money_str(cash)
        payload["cash_after_payroll"] = money_str(cash - employment)
        payload["cash_note"] = (
            "Cash is the sum of recorded demonstration book entries. "
            "No bank or mobile-money settlement has been executed."
        )
    return payload

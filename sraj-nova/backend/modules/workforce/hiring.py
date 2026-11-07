from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from modules.organization.models import ClientSite, Department, JobPosition
from modules.workforce.models import (
    Applicant,
    ApplicantStatus,
    Deployment,
    Employee,
    EmploymentContract,
    LegalEmployerKind,
    PayProfile,
    Qualification,
    RecruitmentEvent,
)


class HiringError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def _rate(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise HiringError("invalid_rate", "Enter the hourly rate in cedis.")
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise HiringError("invalid_rate", "The hourly rate has to be above zero.")
    return amount


def _placement(site_id, department_id, position_id):
    site = ClientSite.objects.select_related("client").filter(pk=site_id).first()
    department = Department.objects.filter(pk=department_id).first()
    position = JobPosition.objects.filter(pk=position_id).first()
    if site is None or department is None or position is None:
        raise HiringError("invalid_placement", "Choose a plant, a department, and a position.")
    if department.site_id != site.id or position.client_id != site.client_id:
        raise HiringError("invalid_placement", "That department or position does not belong to the selected plant.")
    return site, department, position


def _next_number() -> str:
    highest = 1000
    for number in Employee.objects.values_list("agency_employee_number", flat=True):
        suffix = str(number).removeprefix("SN-")
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"SN-{highest + 1}"


def _clean_name(value, label: str) -> str:
    name = (value or "").strip()
    if not name:
        raise HiringError("invalid_name", f"Enter the {label}.")
    return name[:80]


@transaction.atomic
def add_staff(*, first_name, last_name, site_id, department_id, position_id, hourly_rate, skill="", summary="Added from the HR desk."):
    site, department, position = _placement(site_id, department_id, position_id)
    rate = _rate(hourly_rate)
    today = timezone.localdate()
    employee = Employee.objects.create(
        agency_employee_number=_next_number(),
        first_name=_clean_name(first_name, "first name"),
        last_name=_clean_name(last_name, "last name"),
        status="active",
    )
    EmploymentContract.objects.create(
        employee=employee,
        legal_employer_kind=LegalEmployerKind.AGENCY,
        legal_employer_client=None,
        starts_on=today,
        is_current=True,
    )
    Deployment.objects.create(
        employee=employee,
        client=site.client,
        site=site,
        department=department,
        position=position,
        starts_on=today,
        is_current=True,
    )
    PayProfile.objects.create(employee=employee, hourly_rate=rate, currency="GHS")
    stored_skill = (skill or position.required_skill or "").strip()[:80]
    if stored_skill:
        Qualification.objects.create(employee=employee, skill=stored_skill)
    RecruitmentEvent.objects.create(employee=employee, summary=summary[:240], occurred_on=today)
    return employee


def applicant_row(applicant: Applicant) -> dict:
    hired = applicant.hired_employee
    return {
        "id": str(applicant.id),
        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "phone": applicant.phone,
        "skill": applicant.skill,
        "status": applicant.status,
        "note": applicant.note,
        "is_demo": applicant.is_demo,
        "client_name": applicant.site.client.legal_name,
        "site_name": applicant.site.name,
        "department": applicant.department.name,
        "position": applicant.position.title,
        "site_id": str(applicant.site_id),
        "department_id": str(applicant.department_id),
        "position_id": str(applicant.position_id),
        "employee_number": hired.agency_employee_number if hired else None,
        "employee_id": str(hired.id) if hired else None,
    }


@transaction.atomic
def add_applicant(*, first_name, last_name, phone, skill, site_id, department_id, position_id, note=""):
    site, department, position = _placement(site_id, department_id, position_id)
    applicant = Applicant.objects.create(
        first_name=_clean_name(first_name, "first name"),
        last_name=_clean_name(last_name, "last name"),
        phone=(phone or "").strip()[:40],
        skill=(skill or position.required_skill or "").strip()[:80],
        site=site,
        department=department,
        position=position,
        note=(note or "").strip()[:240],
        status=ApplicantStatus.APPLIED,
    )
    return applicant


def set_applicant_status(applicant: Applicant, status: str) -> None:
    allowed = {ApplicantStatus.SCREENING, ApplicantStatus.OFFERED, ApplicantStatus.REJECTED}
    if applicant.status == ApplicantStatus.HIRED:
        raise HiringError("already_hired", "This person is already on the staff list.")
    if status not in allowed:
        raise HiringError("invalid_status", "Choose screening, offered, or rejected.")
    applicant.status = status
    applicant.save(update_fields=["status", "updated_at"])


@transaction.atomic
def hire_applicant(applicant: Applicant, hourly_rate) -> Employee:
    if applicant.status == ApplicantStatus.HIRED or applicant.hired_employee_id:
        raise HiringError("already_hired", "This person is already on the staff list.")
    if applicant.status == ApplicantStatus.REJECTED:
        raise HiringError("rejected", "A rejected application cannot be hired. Add them again if the decision changed.")
    employee = add_staff(
        first_name=applicant.first_name,
        last_name=applicant.last_name,
        site_id=applicant.site_id,
        department_id=applicant.department_id,
        position_id=applicant.position_id,
        hourly_rate=hourly_rate,
        skill=applicant.skill,
        summary=f"Hired from the recruitment portal for {applicant.position.title}.",
    )
    applicant.status = ApplicantStatus.HIRED
    applicant.hired_employee = employee
    applicant.save(update_fields=["status", "hired_employee", "updated_at"])
    return employee

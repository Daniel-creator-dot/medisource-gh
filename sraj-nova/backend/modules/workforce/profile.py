from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import ok
from modules.identity.models import AGENCY_ROLES, AgencyRole
from modules.operations.models import AttendanceEvent
from modules.operations.services import scoped_employees
from modules.workforce.models import Employee


def employee_profile(user, employee: Employee) -> dict:
    include_private = user.role in AGENCY_ROLES or (
        user.role == AgencyRole.EMPLOYEE and user.employee_id == employee.id
    )
    contract = employee.contracts.filter(is_current=True).select_related("legal_employer_client").first()
    deployments = employee.deployments.select_related("client", "site", "department", "position").order_by("-starts_on")
    notes = employee.hr_notes.all() if include_private else employee.hr_notes.filter(visibility="standard")
    payload = {
        "id": str(employee.id),
        "agency_employee_number": employee.agency_employee_number,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "status": employee.status,
        "is_demo": employee.is_demo,
        "legal_employer": None
        if contract is None or not include_private
        else {
            "kind": contract.legal_employer_kind,
            "client_name": None if contract.legal_employer_client is None else contract.legal_employer_client.legal_name,
            "starts_on": contract.starts_on.isoformat(),
        },
        "deployments": [
            {
                "client_name": row.client.legal_name,
                "site_name": row.site.name,
                "department": row.department.name,
                "position": row.position.title,
                "starts_on": row.starts_on.isoformat(),
                "is_current": row.is_current,
            }
            for row in deployments
        ],
        "qualifications": [row.skill for row in employee.qualifications.all()],
        "attendance": [
            {"occurred_at": event.occurred_at.isoformat(), "event_type": event.event_type, "source": event.source}
            for event in AttendanceEvent.objects.filter(employee=employee).order_by("-occurred_at")[:10]
        ],
        "leave": [
            {"starts_on": row.starts_on.isoformat(), "ends_on": row.ends_on.isoformat(), "status": row.status}
            for row in employee.leave_requests.all()
        ],
        "payments": {"status": "none", "message": "No salary disbursement has been executed."},
        "pay_profile": None,
        "certifications": [],
        "recruitment": [],
        "hr_notes": [{"visibility": row.visibility, "body": row.body} for row in notes],
    }
    if include_private:
        profile = getattr(employee, "pay_profile", None)
        if profile is not None:
            payload["pay_profile"] = {"hourly_rate": format(profile.hourly_rate, "f"), "currency": profile.currency}
        payload["certifications"] = [
            {"name": row.name, "expires_on": None if row.expires_on is None else row.expires_on.isoformat()}
            for row in employee.certifications.all()
        ]
        payload["recruitment"] = [
            {"occurred_on": row.occurred_on.isoformat(), "summary": row.summary} for row in employee.recruitment_events.all()
        ]
    return payload


class EmployeeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):
        employee = scoped_employees(request.user).filter(pk=employee_id).first()
        if employee is None:
            raise NotFound()
        return ok(employee_profile(request.user, employee))

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import ok
from modules.identity.models import AgencyRole
from modules.operations.services import scoped_employees
from modules.workforce.models import Employee


def _employee_payload(employee: Employee, *, include_employer: bool) -> dict:
    contract = employee.contracts.filter(is_current=True).select_related("legal_employer_client").first()
    deployment = employee.deployments.filter(is_current=True).select_related("client", "site", "department", "position").first()
    payload = {
        "id": str(employee.id),
        "agency_employee_number": employee.agency_employee_number,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "status": employee.status,
        "is_demo": employee.is_demo,
        "deployment": None
        if deployment is None
        else {
            "client_name": deployment.client.legal_name,
            "site_name": deployment.site.name,
            "department": deployment.department.name,
            "position": deployment.position.title,
        },
    }
    if include_employer and contract is not None:
        payload["legal_employer"] = {
            "kind": contract.legal_employer_kind,
            "client_name": None if contract.legal_employer_client is None else contract.legal_employer_client.legal_name,
        }
    return payload


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.CLIENT_USER:
            include_employer = False
        elif request.user.role == AgencyRole.EMPLOYEE:
            include_employer = True
        else:
            include_employer = True
        employees = scoped_employees(request.user).prefetch_related("contracts", "deployments")
        return ok([_employee_payload(employee, include_employer=include_employer) for employee in employees])


class MyEmploymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.employee_id is None:
            raise PermissionDenied()
        employee = Employee.objects.filter(pk=request.user.employee_id).first()
        if employee is None:
            raise NotFound()
        return ok(_employee_payload(employee, include_employer=True))

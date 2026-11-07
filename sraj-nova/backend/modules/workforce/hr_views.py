from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.identity.models import AGENCY_ROLES
from modules.workforce.hiring import HiringError, add_applicant, add_staff, applicant_row, hire_applicant, set_applicant_status
from modules.workforce.models import Applicant


def _agency(user):
    if user.role not in AGENCY_ROLES:
        raise PermissionDenied()


class AddStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _agency(request.user)
        try:
            employee = add_staff(
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                site_id=request.data.get("site_id"),
                department_id=request.data.get("department_id"),
                position_id=request.data.get("position_id"),
                hourly_rate=request.data.get("hourly_rate"),
                skill=request.data.get("skill") or "",
            )
        except HiringError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(
            {
                "id": str(employee.id),
                "agency_employee_number": employee.agency_employee_number,
                "name": f"{employee.first_name} {employee.last_name}",
            },
            status=201,
        )


class ApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _agency(request.user)
        applicants = Applicant.objects.select_related("site__client", "department", "position", "hired_employee")
        return ok([applicant_row(applicant) for applicant in applicants])

    def post(self, request):
        _agency(request.user)
        try:
            applicant = add_applicant(
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                phone=request.data.get("phone") or "",
                skill=request.data.get("skill") or "",
                site_id=request.data.get("site_id"),
                department_id=request.data.get("department_id"),
                position_id=request.data.get("position_id"),
                note=request.data.get("note") or "",
            )
        except HiringError as exc:
            return error_response(exc.code, exc.message, 400)
        applicant = Applicant.objects.select_related("site__client", "department", "position", "hired_employee").get(pk=applicant.pk)
        return ok(applicant_row(applicant), status=201)


class ApplicantStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, applicant_id):
        _agency(request.user)
        applicant = Applicant.objects.filter(pk=applicant_id).first()
        if applicant is None:
            raise NotFound()
        try:
            set_applicant_status(applicant, request.data.get("status") or "")
        except HiringError as exc:
            return error_response(exc.code, exc.message, 400)
        applicant = Applicant.objects.select_related("site__client", "department", "position", "hired_employee").get(pk=applicant.pk)
        return ok(applicant_row(applicant))


class HireApplicantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, applicant_id):
        _agency(request.user)
        applicant = Applicant.objects.filter(pk=applicant_id).first()
        if applicant is None:
            raise NotFound()
        try:
            employee = hire_applicant(applicant, request.data.get("hourly_rate"))
        except HiringError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(
            {
                "id": str(employee.id),
                "agency_employee_number": employee.agency_employee_number,
                "name": f"{employee.first_name} {employee.last_name}",
            },
            status=201,
        )

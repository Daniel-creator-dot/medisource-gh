from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.identity.models import AGENCY_ROLES, AgencyRole
from modules.operations.coverage import assignment_block, coverage
from modules.operations.models import AttendanceAdjustment, AttendanceEvent, ShiftAssignment
from modules.operations.services import factory_floor, scoped_clients
from modules.workforce.models import Employee


class AttendanceAdjustmentView(APIView):
    """Record a correction without changing the original device event."""

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        if request.user.role not in AGENCY_ROLES:
            raise PermissionDenied()
        event = AttendanceEvent.objects.filter(pk=event_id).first()
        if event is None:
            raise NotFound()
        reason = (request.data.get("reason") or "").strip()
        if not reason:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"reason": "A reason is required."})
        original = event.occurred_at
        adjustment = AttendanceAdjustment.objects.create(event=event, reason=reason)
        event.refresh_from_db()
        return ok(
            {
                "adjustment_id": str(adjustment.id),
                "event_id": str(event.id),
                "occurred_at_unchanged": event.occurred_at == original,
            },
            status=201,
        )


class FactoryFloorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        return ok(factory_floor(request.user))


class CoverageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        allowed = set(scoped_clients(request.user).values_list("legal_name", flat=True))
        return ok([row for row in coverage() if row["client_name"] in allowed])


class AssignShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, shift_id):
        if request.user.role not in AGENCY_ROLES:
            raise PermissionDenied()
        shift = ShiftAssignment.objects.filter(pk=shift_id).select_related("position").first()
        if shift is None:
            raise NotFound()
        if shift.employee_id is not None:
            return error_response("already_filled", "This shift already has a worker.", 409)
        employee = Employee.objects.filter(pk=request.data.get("employee_id")).first()
        if employee is None:
            raise NotFound()
        reason = assignment_block(employee, shift)
        if reason:
            return error_response("assignment_blocked", reason, 400)
        shift.employee = employee
        shift.save(update_fields=["employee", "updated_at"])
        from modules.finance.services import rebuild_week_invoices

        rebuild_week_invoices()
        return ok({"shift_id": str(shift.id), "employee_number": employee.agency_employee_number})

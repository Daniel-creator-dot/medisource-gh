from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.identity.models import AGENCY_ROLES, AgencyRole
from modules.operations.coverage import assignment_block, coverage
from modules.operations.models import (
    AttendanceAdjustment,
    AttendanceEvent,
    AttendanceSource,
    ShiftAssignment,
    StaffingRequest,
)
from modules.operations.services import department_board, factory_floor, scoped_clients, scoped_employees
from modules.organization.models import ClientSite, Department, JobPosition
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


class DepartmentBoardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        return ok(department_board(request.user))


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


class WorkOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clients = scoped_clients(request.user)
        sites = ClientSite.objects.filter(client__in=clients).select_related("client").prefetch_related("departments")
        positions = JobPosition.objects.filter(client__in=clients)
        workers = scoped_employees(request.user)
        return ok(
            {
                "can_open_shift": request.user.role in AGENCY_ROLES,
                "can_record_attendance": request.user.role != AgencyRole.CLIENT_USER,
                "can_request_staff": request.user.role != AgencyRole.EMPLOYEE,
                "sites": [
                    {
                        "id": str(site.id),
                        "client_id": str(site.client_id),
                        "client_name": site.client.legal_name,
                        "name": site.name,
                        "city": site.city,
                        "departments": [{"id": str(department.id), "name": department.name} for department in site.departments.all()],
                    }
                    for site in sites
                ],
                "positions": [
                    {
                        "id": str(position.id),
                        "client_id": str(position.client_id),
                        "title": position.title,
                        "required_skill": position.required_skill,
                    }
                    for position in positions
                ],
                "workers": [
                    {"id": str(worker.id), "number": worker.agency_employee_number, "name": f"{worker.first_name} {worker.last_name}"}
                    for worker in workers
                ],
            }
        )


class OpenShiftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in AGENCY_ROLES:
            raise PermissionDenied()
        site = ClientSite.objects.filter(pk=request.data.get("site_id"), client__in=scoped_clients(request.user)).select_related("client").first()
        department = Department.objects.filter(pk=request.data.get("department_id")).first()
        position = JobPosition.objects.filter(pk=request.data.get("position_id")).first()
        work_date = parse_date(str(request.data.get("work_date") or ""))
        starts = parse_time(str(request.data.get("starts_at") or ""))
        ends = parse_time(str(request.data.get("ends_at") or ""))
        if site is None or department is None or position is None or work_date is None or starts is None or ends is None:
            return error_response("invalid_shift", "Choose a site, department, position, date, and both times.", 400)
        if department.site_id != site.id or position.client_id != site.client_id:
            return error_response("invalid_shift", "That department or position does not belong to the selected factory.", 400)
        employee = None
        if request.data.get("employee_id"):
            employee = scoped_employees(request.user).filter(pk=request.data.get("employee_id")).first()
            if employee is None:
                raise NotFound()
        shift = ShiftAssignment(
            client=site.client,
            site=site,
            department=department,
            position=position,
            employee=employee,
            work_date=work_date,
            starts_at=starts,
            ends_at=ends,
        )
        if employee is not None:
            reason = assignment_block(employee, shift)
            if reason:
                return error_response("assignment_blocked", reason, 400)
        shift.save()
        if employee is not None:
            from modules.finance.services import rebuild_week_invoices

            rebuild_week_invoices(work_date)
        return ok({"shift_id": str(shift.id), "employee_number": None if employee is None else employee.agency_employee_number}, status=201)


class RecordAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role == AgencyRole.CLIENT_USER:
            raise PermissionDenied()
        event_type = request.data.get("event_type")
        if event_type not in {"in", "out"}:
            return error_response("invalid_punch", "Choose arrival or departure.", 400)
        if request.user.role == AgencyRole.EMPLOYEE:
            employee = scoped_employees(request.user).first()
        else:
            employee = scoped_employees(request.user).filter(pk=request.data.get("employee_id")).first()
        if employee is None:
            raise NotFound()
        raw = request.data.get("occurred_at")
        if raw:
            occurred = parse_datetime(str(raw))
            if occurred is None:
                return error_response("invalid_punch", "The punch time could not be read.", 400)
            if timezone.is_naive(occurred):
                occurred = timezone.make_aware(occurred, timezone.get_current_timezone())
        else:
            occurred = timezone.now()
        event = AttendanceEvent.objects.create(
            employee=employee,
            occurred_at=occurred,
            event_type=event_type,
            source=AttendanceSource.MOBILE if request.user.role == AgencyRole.EMPLOYEE else AttendanceSource.SUPERVISOR,
        )
        local = timezone.localtime(occurred)
        return ok(
            {
                "event_id": str(event.id),
                "worker_number": employee.agency_employee_number,
                "event_type": event.event_type,
                "occurred_at": local.isoformat(),
            },
            status=201,
        )


class StaffingRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        site = ClientSite.objects.filter(pk=request.data.get("site_id"), client__in=scoped_clients(request.user)).select_related("client").first()
        title = str(request.data.get("title") or "").strip()
        try:
            headcount = int(request.data.get("headcount") or 0)
        except (TypeError, ValueError):
            headcount = 0
        if site is None or not title or headcount < 1:
            return error_response("invalid_request", "Choose a factory, describe the post, and enter at least one worker.", 400)
        request_row = StaffingRequest.objects.create(client=site.client, site=site, title=title, headcount=headcount)
        return ok({"id": str(request_row.id), "title": request_row.title, "headcount": request_row.headcount, "status": request_row.status}, status=201)

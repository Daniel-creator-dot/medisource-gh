from django.urls import path

from modules.operations.views import (
    AssignShiftView,
    AttendanceAdjustmentView,
    CoverageView,
    DepartmentBoardView,
    FactoryFloorView,
    OpenShiftView,
    RecordAttendanceView,
    StaffingRequestView,
    WorkOptionsView,
)

urlpatterns = [
    path("departments/", DepartmentBoardView.as_view(), name="departments"),
    path("factory-floor/", FactoryFloorView.as_view(), name="factory-floor"),
    path("work/options/", WorkOptionsView.as_view(), name="work-options"),
    path("shifts/", OpenShiftView.as_view(), name="open-shift"),
    path("attendance/", RecordAttendanceView.as_view(), name="record-attendance"),
    path("staffing-requests/", StaffingRequestView.as_view(), name="staffing-request"),
    path("attendance-events/<uuid:event_id>/adjustments/", AttendanceAdjustmentView.as_view(), name="attendance-adjustment"),
    path("deployment/coverage/", CoverageView.as_view(), name="coverage"),
    path("shifts/<uuid:shift_id>/assign/", AssignShiftView.as_view(), name="assign-shift"),
]

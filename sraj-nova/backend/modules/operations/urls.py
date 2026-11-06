from django.urls import path

from modules.operations.views import AssignShiftView, AttendanceAdjustmentView, CoverageView, FactoryFloorView

urlpatterns = [
    path("factory-floor/", FactoryFloorView.as_view(), name="factory-floor"),
    path("attendance-events/<uuid:event_id>/adjustments/", AttendanceAdjustmentView.as_view(), name="attendance-adjustment"),
    path("deployment/coverage/", CoverageView.as_view(), name="coverage"),
    path("shifts/<uuid:shift_id>/assign/", AssignShiftView.as_view(), name="assign-shift"),
]

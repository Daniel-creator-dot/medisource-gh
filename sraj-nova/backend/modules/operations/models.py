from django.db import models

from common.models import UUIDModel


class ShiftAssignment(UUIDModel):
    client = models.ForeignKey("organization.Client", on_delete=models.PROTECT, related_name="shifts")
    site = models.ForeignKey("organization.ClientSite", on_delete=models.PROTECT, related_name="shifts")
    department = models.ForeignKey("organization.Department", on_delete=models.PROTECT, related_name="shifts")
    position = models.ForeignKey("organization.JobPosition", on_delete=models.PROTECT, related_name="shifts")
    employee = models.ForeignKey(
        "workforce.Employee",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="shifts",
    )
    work_date = models.DateField()
    starts_at = models.TimeField()
    ends_at = models.TimeField()

    class Meta:
        ordering = ["work_date", "starts_at"]


class AttendanceSource(models.TextChoices):
    DEVICE_IMPORT = "device_import", "Device import"
    MOBILE = "mobile", "Mobile"
    SUPERVISOR = "supervisor", "Supervisor"


class AttendanceEvent(UUIDModel):
    employee = models.ForeignKey("workforce.Employee", on_delete=models.PROTECT, related_name="attendance_events")
    occurred_at = models.DateTimeField()
    event_type = models.CharField(max_length=8)
    source = models.CharField(max_length=32, choices=AttendanceSource.choices)
    device_reference = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["occurred_at"]


class AttendanceAdjustment(UUIDModel):
    event = models.ForeignKey(AttendanceEvent, on_delete=models.PROTECT, related_name="adjustments")
    reason = models.TextField()
    status = models.CharField(max_length=16, default="pending")


class StaffingRequest(UUIDModel):
    client = models.ForeignKey("organization.Client", on_delete=models.PROTECT, related_name="staffing_requests")
    site = models.ForeignKey("organization.ClientSite", on_delete=models.PROTECT, related_name="staffing_requests")
    title = models.CharField(max_length=160)
    headcount = models.PositiveIntegerField()
    status = models.CharField(max_length=16, default="pending")
    is_demo = models.BooleanField(default=False)


class OperationalAlert(UUIDModel):
    client = models.ForeignKey(
        "organization.Client",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    severity = models.CharField(max_length=16)
    message = models.CharField(max_length=240)
    is_open = models.BooleanField(default=True)

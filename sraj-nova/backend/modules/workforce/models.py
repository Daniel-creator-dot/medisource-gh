from decimal import Decimal

from django.db import models

from common.models import UUIDModel


class EmployeeStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    ON_LEAVE = "on_leave", "On leave"
    RESIGNED = "resigned", "Resigned"
    TERMINATED = "terminated", "Terminated"


class LegalEmployerKind(models.TextChoices):
    AGENCY = "agency", "SRAJ NOVA"
    CLIENT = "client", "Client organization"


class Employee(UUIDModel):
    agency_employee_number = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    is_demo = models.BooleanField(default=False)

    class Meta:
        ordering = ["agency_employee_number"]

    def __str__(self) -> str:
        return f"{self.agency_employee_number} {self.first_name} {self.last_name}"


class EmployeeIdentifier(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="identifiers")
    kind = models.CharField(max_length=32)
    ciphertext = models.TextField()
    is_synthetic = models.BooleanField(default=True)


class EmploymentContract(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="contracts")
    legal_employer_kind = models.CharField(max_length=16, choices=LegalEmployerKind.choices)
    legal_employer_client = models.ForeignKey(
        "organization.Client",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="employment_contracts",
    )
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(legal_employer_kind="agency", legal_employer_client__isnull=True)
                    | models.Q(legal_employer_kind="client", legal_employer_client__isnull=False)
                ),
                name="legal_employer_matches_kind",
            )
        ]


class Deployment(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="deployments")
    client = models.ForeignKey("organization.Client", on_delete=models.PROTECT, related_name="deployments")
    site = models.ForeignKey("organization.ClientSite", on_delete=models.PROTECT, related_name="deployments")
    department = models.ForeignKey("organization.Department", on_delete=models.PROTECT, related_name="deployments")
    position = models.ForeignKey("organization.JobPosition", on_delete=models.PROTECT, related_name="deployments")
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)


class PayProfile(UUIDModel):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="pay_profile")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")


class Qualification(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="qualifications")
    skill = models.CharField(max_length=80)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["employee", "skill"], name="unique_employee_skill")]


class Certification(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=160)
    expires_on = models.DateField(null=True, blank=True)


class LeaveRequest(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_requests")
    starts_on = models.DateField()
    ends_on = models.DateField()
    status = models.CharField(max_length=16, default="approved")


class RecruitmentEvent(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="recruitment_events")
    summary = models.CharField(max_length=240)
    occurred_on = models.DateField()


class ApplicantStatus(models.TextChoices):
    APPLIED = "applied", "Applied"
    SCREENING = "screening", "Screening"
    OFFERED = "offered", "Offered"
    HIRED = "hired", "Hired"
    REJECTED = "rejected", "Rejected"


class Applicant(UUIDModel):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=40, blank=True)
    skill = models.CharField(max_length=80, blank=True)
    site = models.ForeignKey("organization.ClientSite", on_delete=models.PROTECT, related_name="applicants")
    department = models.ForeignKey("organization.Department", on_delete=models.PROTECT, related_name="applicants")
    position = models.ForeignKey("organization.JobPosition", on_delete=models.PROTECT, related_name="applicants")
    status = models.CharField(max_length=16, choices=ApplicantStatus.choices, default=ApplicantStatus.APPLIED)
    note = models.CharField(max_length=240, blank=True)
    hired_employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.PROTECT, related_name="application")
    is_demo = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class HrNote(UUIDModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="hr_notes")
    visibility = models.CharField(max_length=16, default="standard")
    body = models.TextField()

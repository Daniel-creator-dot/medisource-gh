from django.conf import settings
from django.db import models

from common.models import UUIDTimeStampedModel


class OrganizationType(models.TextChoices):
    SUPPLIER = "supplier", "Supplier"
    FACILITY = "facility", "Facility"
    PLATFORM = "platform", "Platform"
    LOGISTICS = "logistics", "Logistics partner"


class OrganizationStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"


class MembershipRole(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    BUYER = "buyer", "Buyer"
    FINANCE = "finance", "Finance"
    CLINICIAN = "clinician", "Clinician"


class Organization(UUIDTimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    org_type = models.CharField(max_length=32, choices=OrganizationType.choices)
    status = models.CharField(
        max_length=32,
        choices=OrganizationStatus.choices,
        default=OrganizationStatus.ACTIVE,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Membership(UUIDTimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=32, choices=MembershipRole.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.organization_id}"

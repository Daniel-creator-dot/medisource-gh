from django.db import models

from common.models import UUIDTimeStampedModel


class ProfessionalVerification(models.TextChoices):
    PENDING = "pending", "Pending"
    VERIFIED = "verified", "Verified"
    SUSPENDED = "suspended", "Suspended"
    DEMO = "demo", "Sample record"


class ProfessionRole(UUIDTimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ProfessionalProfile(UUIDTimeStampedModel):
    role = models.ForeignKey(ProfessionRole, on_delete=models.PROTECT, related_name="profiles")
    display_name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=120, unique=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    summary = models.TextField()
    verification_status = models.CharField(
        max_length=32,
        choices=ProfessionalVerification.choices,
        default=ProfessionalVerification.PENDING,
    )
    is_demo = models.BooleanField(default=False)
    credential_expires_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name

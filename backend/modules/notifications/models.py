from django.conf import settings
from django.db import models

from common.models import UUIDTimeStampedModel


class Notification(UUIDTimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=160)
    body = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class ContactInquiry(UUIDTimeStampedModel):
    class Topic(models.TextChoices):
        GENERAL = "general", "General"
        SUPPLIER = "supplier", "Supplier"
        FACILITY = "facility", "Facility"
        SUPPORT = "support", "Support"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    organization_name = models.CharField(max_length=200, blank=True)
    topic = models.CharField(max_length=32, choices=Topic.choices)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

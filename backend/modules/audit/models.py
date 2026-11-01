from django.conf import settings
from django.db import models

from common.models import UUIDTimeStampedModel


class AuditLog(UUIDTimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} {self.resource_type}"

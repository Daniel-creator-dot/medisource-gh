from django.conf import settings
from django.db import models

from common.models import UUIDModel


class AuditEvent(UUIDModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    action = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=80)
    resource_id = models.CharField(max_length=64, blank=True)


class OutboxMessage(UUIDModel):
    topic = models.CharField(max_length=80)
    payload = models.JSONField()
    published_at = models.DateTimeField(null=True, blank=True)

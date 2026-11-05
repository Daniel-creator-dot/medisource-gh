from django.db import transaction

from modules.governance.models import AuditEvent, OutboxMessage


@transaction.atomic
def record_audit(*, actor, action: str, resource_type: str, resource_id) -> None:
    AuditEvent.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
    )
    OutboxMessage.objects.create(
        topic=action,
        payload={"resource_type": resource_type, "resource_id": str(resource_id)},
    )

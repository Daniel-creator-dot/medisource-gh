def record_audit(
    *,
    action: str,
    resource_type: str,
    actor=None,
    resource_id: str = "",
    metadata: dict | None = None,
    request=None,
):
    from modules.audit.models import AuditLog

    ip_address = None
    user_agent = ""
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else "",
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )

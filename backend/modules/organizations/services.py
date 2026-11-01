from django.db import transaction

from modules.audit.services import record_audit
from modules.organizations.models import Membership, Organization


def create_organization(*, name: str, slug: str, org_type: str, owner, role: str) -> Organization:
    with transaction.atomic():
        organization = Organization.objects.create(name=name, slug=slug, org_type=org_type)
        Membership.objects.create(
            user=owner,
            organization=organization,
            role=role,
            is_active=True,
        )
        record_audit(
            actor=owner,
            action="organization.created",
            resource_type="organization",
            resource_id=organization.id,
            metadata={"org_type": org_type},
        )
        return organization


def active_membership(user, organization) -> Membership | None:
    if not getattr(user, "is_authenticated", False):
        return None
    return Membership.objects.filter(user=user, organization=organization, is_active=True).first()

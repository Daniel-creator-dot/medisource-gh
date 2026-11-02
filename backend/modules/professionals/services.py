from django.db.models import Q
from django.utils import timezone

from modules.professionals.constants import PROFESSION_ROLES
from modules.professionals.models import ProfessionRole, ProfessionalProfile, ProfessionalVerification


def ensure_profession_roles() -> None:
    for index, (slug, name, description) in enumerate(PROFESSION_ROLES, start=1):
        ProfessionRole.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "description": description, "sort_order": index},
        )


def public_professionals(params):
    today = timezone.localdate()
    queryset = ProfessionalProfile.objects.filter(
        verification_status=ProfessionalVerification.VERIFIED,
        is_demo=False,
        credential_expires_on__gte=today,
    ).select_related("role")
    query = (params.get("q") or "").strip()
    if query:
        queryset = queryset.filter(
            Q(display_name__icontains=query) | Q(summary__icontains=query) | Q(city__icontains=query)
        )
    role = (params.get("role") or "").strip()
    if role:
        queryset = queryset.filter(role__slug=role)
    region = (params.get("region") or "").strip()
    if region:
        queryset = queryset.filter(region__iexact=region)
    return queryset.order_by("display_name")

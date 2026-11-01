import pytest

from conftest import bearer
from modules.audit.models import AuditLog
from modules.identity.models import PlatformRole
from modules.organizations.models import MembershipRole, OrganizationType
from modules.organizations.services import create_organization
from tests.factories import make_user


@pytest.mark.django_db
def test_members_are_isolated_and_admin_views_are_audited(api):
    owner = make_user(email="owner@example.com")
    stranger = make_user(email="stranger@example.com")
    admin = make_user(email="admin@example.com", platform_role=PlatformRole.PLATFORM_ADMIN)
    organization = create_organization(
        name="Harbour",
        slug="harbour",
        org_type=OrganizationType.SUPPLIER,
        owner=owner,
        role=MembershipRole.OWNER,
    )

    bearer(api, stranger)
    assert api.get(f"/api/v1/organizations/{organization.id}/").status_code == 404

    bearer(api, owner)
    assert api.get(f"/api/v1/organizations/{organization.id}/").status_code == 200
    memberships = api.get("/api/v1/account/memberships/")
    assert memberships.json()["data"][0]["organization"]["slug"] == "harbour"

    bearer(api, admin)
    assert api.get(f"/api/v1/organizations/{organization.id}/").status_code == 200
    assert AuditLog.objects.filter(action="organization.admin_view", actor=admin).exists()

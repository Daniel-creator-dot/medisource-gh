from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from modules.professionals.models import ProfessionalProfile, ProfessionalVerification
from modules.professionals.services import ensure_profession_roles


@pytest.mark.django_db
def test_directory_lists_only_current_verified_professionals(api):
    ensure_profession_roles()
    role = api.get("/api/v1/professionals/roles/").json()["data"]["roles"][0]
    shared = {
        "role_id": role["id"],
        "city": "Accra",
        "region": "Greater Accra",
        "summary": "Reviewed profile.",
    }
    ProfessionalProfile.objects.create(
        display_name="Sample Person",
        slug="sample-person",
        verification_status=ProfessionalVerification.DEMO,
        is_demo=True,
        credential_expires_on=timezone.localdate() + timedelta(days=30),
        **shared,
    )
    ProfessionalProfile.objects.create(
        display_name="Pending Person",
        slug="pending-person",
        verification_status=ProfessionalVerification.PENDING,
        is_demo=False,
        credential_expires_on=timezone.localdate() + timedelta(days=30),
        **shared,
    )
    ProfessionalProfile.objects.create(
        display_name="Expired Person",
        slug="expired-person",
        verification_status=ProfessionalVerification.VERIFIED,
        is_demo=False,
        credential_expires_on=timezone.localdate() - timedelta(days=1),
        **shared,
    )
    hidden = api.get("/api/v1/professionals/")
    assert hidden.status_code == 200
    assert hidden.json()["data"] == []

    ProfessionalProfile.objects.create(
        display_name="Ama Mensah",
        slug="ama-mensah",
        verification_status=ProfessionalVerification.VERIFIED,
        is_demo=False,
        credential_expires_on=timezone.localdate() + timedelta(days=30),
        **shared,
    )
    listed = api.get("/api/v1/professionals/?role=doctor&region=Greater%20Accra")
    assert [item["slug"] for item in listed.json()["data"]] == ["ama-mensah"]
    assert "licence" not in listed.content.decode().lower()
    missed = api.get("/api/v1/professionals/?region=Ashanti")
    assert missed.json()["data"] == []


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_seed_creates_roles_and_no_sample_clinicians():
    call_command("seed_demo")
    from modules.professionals.models import ProfessionRole

    assert ProfessionRole.objects.count() == 9
    assert ProfessionalProfile.objects.count() == 0

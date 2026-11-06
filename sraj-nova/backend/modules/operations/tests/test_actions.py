import pytest
from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.identity.models import User
from modules.operations.models import AttendanceEvent, ShiftAssignment, StaffingRequest
from modules.organization.models import ClientSite, Department, JobPosition


def auth(api, user):
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_agency_can_open_a_post_and_a_client_cannot(api):
    call_command("seed_demo")
    site = ClientSite.objects.filter(client__slug="sample-ashanti-textile").first()
    department = Department.objects.filter(site=site).first()
    position = JobPosition.objects.filter(client=site.client).first()
    day = timezone.localdate()
    week_end = day - timedelta(days=day.weekday()) + timedelta(days=6)
    payload = {
        "site_id": str(site.id),
        "department_id": str(department.id),
        "position_id": str(position.id),
        "work_date": week_end.isoformat(),
        "starts_at": "06:00",
        "ends_at": "14:00",
    }
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    assert api.post("/api/v1/shifts/", payload, format="json").status_code == 403
    auth(api, User.objects.get(email="nova.ops@sample.sraj.test"))
    created = api.post("/api/v1/shifts/", payload, format="json")
    assert created.status_code == 201
    assert ShiftAssignment.objects.filter(pk=created.json()["data"]["shift_id"], employee__isnull=True).exists()
    coverage = api.get("/api/v1/deployment/coverage/").json()["data"]
    assert any(row["shift_id"] == created.json()["data"]["shift_id"] for row in coverage)


@pytest.mark.django_db
def test_worker_punch_is_stored_and_cannot_punch_someone_else(api):
    call_command("seed_demo")
    before = AttendanceEvent.objects.count()
    auth(api, User.objects.get(email="worker.ama@sample.sraj.test"))
    punched = api.post("/api/v1/attendance/", {"event_type": "out"}, format="json")
    assert punched.status_code == 201
    assert punched.json()["data"]["worker_number"] == "SN-1001"
    assert AttendanceEvent.objects.count() == before + 1
    other = api.post("/api/v1/attendance/", {"event_type": "in", "employee_id": "00000000-0000-0000-0000-000000000000"}, format="json")
    assert other.status_code == 201
    assert other.json()["data"]["worker_number"] == "SN-1001"


@pytest.mark.django_db
def test_client_can_request_staff_only_for_their_factory(api):
    call_command("seed_demo")
    own = ClientSite.objects.filter(client__slug="sample-ashanti-textile").first()
    other = ClientSite.objects.filter(client__slug="sample-tema-logistics").first()
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    refused = api.post("/api/v1/staffing-requests/", {"site_id": str(other.id), "title": "Night weavers", "headcount": 2}, format="json")
    assert refused.status_code == 400
    accepted = api.post("/api/v1/staffing-requests/", {"site_id": str(own.id), "title": "Night weavers", "headcount": 2}, format="json")
    assert accepted.status_code == 201
    assert StaffingRequest.objects.filter(title="Night weavers", client__slug="sample-ashanti-textile").exists()

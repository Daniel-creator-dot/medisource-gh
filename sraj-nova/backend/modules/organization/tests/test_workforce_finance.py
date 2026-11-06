import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.identity.models import User
from modules.workforce.models import Employee


def auth(api, user):
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_employee_profile_hides_pay_and_restricted_notes_from_the_client(api):
    call_command("seed_demo")
    ama = Employee.objects.get(agency_employee_number="SN-1001")
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    body = api.get(f"/api/v1/employees/{ama.id}/").json()["data"]
    assert body["pay_profile"] is None
    assert body["recruitment"] == []
    assert all(note["visibility"] == "standard" for note in body["hr_notes"])
    assert "SAMPLE-NOT-A-REAL-ID" not in api.get(f"/api/v1/employees/{ama.id}/").content.decode()
    yaw = Employee.objects.get(agency_employee_number="SN-2001")
    assert api.get(f"/api/v1/employees/{yaw.id}/").status_code == 404


@pytest.mark.django_db
def test_worker_sees_own_profile_and_not_another(api):
    call_command("seed_demo")
    auth(api, User.objects.get(email="worker.ama@sample.sraj.test"))
    mine = api.get("/api/v1/me/employment/")
    profile = api.get(f"/api/v1/employees/{mine.json()['data']['id']}/")
    assert profile.json()["data"]["pay_profile"]["hourly_rate"] == "20.00"
    assert profile.json()["data"]["payments"]["status"] == "none"
    assert any(note["visibility"] == "restricted" for note in profile.json()["data"]["hr_notes"])
    other = Employee.objects.get(agency_employee_number="SN-1002")
    assert api.get(f"/api/v1/employees/{other.id}/").status_code == 404


@pytest.mark.django_db
def test_coverage_recommends_only_a_rested_skilled_worker_and_blocks_assignment(api):
    call_command("seed_demo")
    auth(api, User.objects.get(email="nova.ops@sample.sraj.test"))
    rows = api.get("/api/v1/deployment/coverage/").json()["data"]
    assert len(rows) == 1
    names = {row["employee_number"] for row in rows[0]["recommendations"]}
    assert names == {"SN-1004"}
    blocked = {row["employee_number"] for row in rows[0]["blocked"]}
    assert blocked == {"SN-1002"}
    ama = Employee.objects.get(agency_employee_number="SN-1001")
    refused = api.post(f"/api/v1/shifts/{rows[0]['shift_id']}/assign/", {"employee_id": str(ama.id)}, format="json")
    assert refused.status_code == 400
    assert "Missing required skill" in refused.json()["error"]["message"]
    kofi = Employee.objects.get(agency_employee_number="SN-1002")
    resting = api.post(f"/api/v1/shifts/{rows[0]['shift_id']}/assign/", {"employee_id": str(kofi.id)}, format="json")
    assert resting.status_code == 400
    assert "11 hours" in resting.json()["error"]["message"]
    abena = Employee.objects.get(agency_employee_number="SN-1004")
    accepted = api.post(f"/api/v1/shifts/{rows[0]['shift_id']}/assign/", {"employee_id": str(abena.id)}, format="json")
    assert accepted.status_code == 200
    assert accepted.json()["data"]["employee_number"] == "SN-1004"
    finance = api.get("/api/v1/finance/").json()["data"]
    assert finance["weekly_gross_payroll"] == "766.00"
    assert finance["agency_fee"] == "89.40"


@pytest.mark.django_db
def test_client_finance_excludes_agency_cash(api):
    call_command("seed_demo")
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    data = api.get("/api/v1/finance/").json()["data"]
    assert data["weekly_gross_payroll"] == "480.00"
    assert data["agency_fee"] == "57.60"
    assert data["outstanding_invoices"] == "537.60"
    assert "cash_available" not in data
    assert data["statutory_liabilities"] is None
    assert api.post("/api/v1/finance/worksheets/rebuild/", {}, format="json").status_code == 403


@pytest.mark.django_db
def test_factory_floor_scopes_sites_and_keeps_rates_with_the_agency(api):
    call_command("seed_demo")
    auth(api, User.objects.get(email="worker.ama@sample.sraj.test"))
    assert api.get("/api/v1/factory-floor/").status_code == 403
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    floor = api.get("/api/v1/factory-floor/").json()["data"]
    assert floor["shifts"]
    assert {row["client_name"] for row in floor["shifts"]} == {"Sample Ashanti Cement Works"}
    assert "hourly_rate" not in floor["shifts"][0]
    finance = api.get("/api/v1/finance/").json()["data"]
    assert finance["sites"]
    assert all(row["client_name"] == "Sample Ashanti Cement Works" for row in finance["sites"])
    auth(api, User.objects.get(email="nova.owner@sample.sraj.test"))
    agency = api.get("/api/v1/factory-floor/").json()["data"]
    priced = next(row for row in agency["shifts"] if row["worker_number"] == "SN-1001")
    assert priced["hourly_rate"] == "20.00"
    assert priced["attendance"] in {"on_duty", "present", "late", "absent"}
    sites = api.get("/api/v1/finance/").json()["data"]["sites"]
    assert sum(1 for row in sites if row["labor_cost"] != "0.00") >= 1

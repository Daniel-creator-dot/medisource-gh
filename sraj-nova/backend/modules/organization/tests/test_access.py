from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.identity.models import AgencyRole, User
from modules.operations.models import AttendanceEvent
from modules.organization.models import Client
from modules.workforce.models import Employee, LegalEmployerKind

PASSWORD = "Nova-Test-Password-1"


def auth(api, user):
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


def make_user(email, role, **extra):
    return User.objects.create_user(email=email, password=PASSWORD, role=role, first_name="Test", last_name="User", **extra)


@pytest.fixture
def api():
    return APIClient(enforce_csrf_checks=True, HTTP_ORIGIN="http://testserver")


@pytest.mark.django_db
def test_client_cannot_see_another_clients_workers(api):
    from django.core.management import call_command

    call_command("seed_demo")
    client_user = User.objects.get(email="client.ashanti@sample.sraj.test")
    auth(api, client_user)
    listed = api.get("/api/v1/employees/")
    numbers = {row["agency_employee_number"] for row in listed.json()["data"]}
    assert numbers == {"SN-1001", "SN-1002", "SN-1003", "SN-1004"}
    assert "SN-2001" not in numbers
    assert api.get("/api/v1/clients/sample-tema-logistics/").status_code == 404
    center = api.get("/api/v1/command-center/")
    names = {row["client_name"] for row in center.json()["data"]["workers_by_client"]}
    assert names == {"Sample Ashanti Cement Works"}
    assert center.json()["data"]["finance"]["weekly_gross_payroll"] == "480.00"
    assert "cash_available" not in center.json()["data"]["finance"]
    board = center.json()["data"]["board"]
    assert board["invoice_weeks"] == [{"week_start": board["attendance_week"][0]["date"], "employment_cost": "480.00", "agency_fee": "57.60", "outstanding": "537.60"}]
    assert board["net_profitability"] is None
    assert all("Tema" not in item["text"] and "opening cash" not in item["text"].lower() for item in board["activity"])
    users = api.get("/api/v1/auth/users/")
    assert users.status_code == 403


@pytest.mark.django_db
def test_employee_sees_only_their_record_and_not_the_command_center(api):
    from django.core.management import call_command

    call_command("seed_demo")
    worker = User.objects.get(email="worker.ama@sample.sraj.test")
    auth(api, worker)
    assert api.get("/api/v1/command-center/").status_code == 403
    assert api.get("/api/v1/clients/").status_code == 403
    mine = api.get("/api/v1/me/employment/")
    assert mine.status_code == 200
    assert mine.json()["data"]["agency_employee_number"] == "SN-1001"
    assert mine.json()["data"]["legal_employer"]["kind"] == LegalEmployerKind.AGENCY
    body = api.get("/api/v1/employees/").content.decode()
    assert "SAMPLE-NOT-A-REAL-ID" not in body
    assert "ciphertext" not in body


@pytest.mark.django_db
def test_command_center_counts_come_from_records(api):
    from django.core.management import call_command

    call_command("seed_demo")
    auth(api, User.objects.get(email="nova.ops@sample.sraj.test"))
    data = api.get("/api/v1/command-center/").json()["data"]
    assert data["active_workforce"] == 5
    assert data["deployed_workers"] == 5
    assert data["scheduled_today"] == 4
    assert data["unfilled_shifts"] == 1
    assert data["on_duty"] == 2
    assert data["late"] == 1
    assert data["absent"] == 1
    assert data["pending_staffing_requests"] == 1
    assert data["expiring_contracts"] == 1
    assert data["open_alerts"]
    kofi = Employee.objects.get(agency_employee_number="SN-1002")
    assert kofi.contracts.get(is_current=True).legal_employer_kind == LegalEmployerKind.CLIENT
    assert data["finance"]["weekly_gross_payroll"] == "606.00"
    assert data["finance"]["agency_fee_revenue"] == "70.20"
    assert data["finance"]["cash_available"] == "2500.00"
    assert data["finance"]["statutory_liabilities"] is None
    assert data["finance"]["estimated_net_payroll"] is None
    week = data["board"]["attendance_week"]
    assert len(week) == 7
    today_row = next(row for row in week if row["is_today"])
    assert today_row["scheduled"] == 4
    assert today_row["unfilled"] == 1
    assert today_row["absent"] == 1
    assert all(row["absent"] is None for row in week if row["future"])
    assert data["board"]["invoice_weeks"][0]["employment_cost"] == "606.00"
    assert data["board"]["invoice_weeks"][0]["agency_fee"] == "70.20"
    assert data["board"]["payroll_approvals"] == []
    assert data["board"]["net_profitability"] is None
    assert any(cell["unfilled"] == 1 for site in data["board"]["heatmap"] for cell in site["days"])


@pytest.mark.django_db
def test_each_cement_department_has_its_own_roster(api):
    from django.core.management import call_command

    call_command("seed_demo")
    auth(api, User.objects.get(email="worker.ama@sample.sraj.test"))
    assert api.get("/api/v1/departments/").status_code == 403
    auth(api, User.objects.get(email="client.ashanti@sample.sraj.test"))
    plants = api.get("/api/v1/departments/").json()["data"]["plants"]
    assert [plant["site_name"] for plant in plants] == ["Ashanti Grinding Plant"]
    departments = {row["name"]: row for row in plants[0]["departments"]}
    assert list(departments) == ["Production", "Packing", "Quality", "Mechanical", "Electrical", "Health and safety"]
    assert departments["Production"]["on_duty"] == 1
    assert departments["Packing"]["roster"] == []
    assert departments["Quality"]["absent"] == 1
    assert departments["Mechanical"]["deployed"] == 2
    assert departments["Mechanical"]["late"] == 1
    assert departments["Mechanical"]["open"] == 1
    assert departments["Electrical"]["roster"] == []
    auth(api, User.objects.get(email="nova.owner@sample.sraj.test"))
    both = api.get("/api/v1/departments/").json()["data"]["plants"]
    assert {plant["site_name"] for plant in both} == {"Ashanti Grinding Plant", "Takoradi Grinding Plant"}


@pytest.mark.django_db
def test_attendance_correction_does_not_change_the_device_event(api):
    from django.core.management import call_command

    call_command("seed_demo")
    event = AttendanceEvent.objects.filter(event_type="in").first()
    original = event.occurred_at
    auth(api, User.objects.get(email="nova.ops@sample.sraj.test"))
    response = api.post(
        f"/api/v1/attendance-events/{event.id}/adjustments/",
        {"reason": "Supervisor review of a sample punch."},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["data"]["occurred_at_unchanged"] is True
    event.refresh_from_db()
    assert event.occurred_at == original


@pytest.mark.django_db
@override_settings(MFA_REQUIRED_FOR_AGENCY_OWNER=True)
def test_agency_owner_without_authenticator_gets_no_session(api):
    user = make_user("owner@example.com", AgencyRole.AGENCY_OWNER)
    csrf = api.get("/api/v1/auth/csrf/")
    token = csrf.json()["data"]["csrf_token"]
    response = api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=token,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "mfa_enrollment_required"
    assert "nova_access" not in api.cookies


@pytest.mark.django_db
def test_schema_setup_skips_sqlite():
    from boot_server import ensure_schema

    ensure_schema()


@pytest.mark.django_db
def test_api_returns_json_when_the_client_asks_for_html(api):
    response = api.get("/api/v1/health/", HTTP_ACCEPT="text/html")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    assert response.json()["data"]["checks"]["database"] == "ok"


@pytest.mark.django_db
def test_csrf_accepts_the_proxy_path_without_a_trailing_slash(api):
    response = api.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    assert response.json()["data"]["csrf_token"]
    from django.core.management import call_command

    call_command("seed_demo")
    health = api.get("/api/v1/health/")
    assert health.status_code == 200
    assert health.json()["data"]["checks"]["database"] == "ok"
    auth(api, User.objects.get(email="nova.owner@sample.sraj.test"))
    agency = api.get("/api/v1/agency/")
    assert agency.json()["data"]["trading_name"] == "SRAJ NOVA"
    users = api.get("/api/v1/auth/users/")
    assert users.status_code == 200
    assert len(users.json()["data"]) == 4
    assert Client.objects.count() == 2
    assert timezone.localdate() + timedelta(days=1)

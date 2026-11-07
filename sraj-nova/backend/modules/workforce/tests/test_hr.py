import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.identity.models import User
from modules.organization.models import Department, JobPosition
from modules.workforce.models import Applicant, Employee


def auth(api, email):
    user = User.objects.get(email=email)
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_hr_can_add_staff_into_a_department_and_a_client_cannot(api):
    call_command("seed_demo")
    site = Department.objects.get(name="Packing", site__name="Ashanti Grinding Plant").site
    department = Department.objects.get(site=site, name="Packing")
    position = JobPosition.objects.get(client=site.client, title="Packing operator")
    payload = {
        "first_name": "Ama",
        "last_name": "Adjei",
        "site_id": str(site.id),
        "department_id": str(department.id),
        "position_id": str(position.id),
        "hourly_rate": "19.50",
        "skill": "packing",
    }
    auth(api, "client.ashanti@sample.sraj.test")
    assert api.post("/api/v1/hr/staff/", payload, format="json").status_code == 403
    auth(api, "nova.ops@sample.sraj.test")
    created = api.post("/api/v1/hr/staff/", payload, format="json")
    assert created.status_code == 201
    number = created.json()["data"]["agency_employee_number"]
    employee = Employee.objects.get(agency_employee_number=number)
    deployment = employee.deployments.get(is_current=True)
    assert deployment.department.name == "Packing"
    assert str(employee.pay_profile.hourly_rate) == "19.50"
    listed = api.get("/api/v1/employees/").json()["data"]
    assert number in {row["agency_employee_number"] for row in listed}


@pytest.mark.django_db
def test_recruitment_hire_creates_one_worker_and_tax_is_not_calculated(api):
    call_command("seed_demo")
    auth(api, "nova.owner@sample.sraj.test")
    applicants = api.get("/api/v1/hr/applicants/").json()["data"]
    sample = next(row for row in applicants if row["last_name"] == "Nyarko")
    assert sample["status"] == "applied"
    assert sample["is_demo"] is True
    hired = api.post(f"/api/v1/hr/applicants/{sample['id']}/hire/", {"hourly_rate": "18.00"}, format="json")
    assert hired.status_code == 201
    again = api.post(f"/api/v1/hr/applicants/{sample['id']}/hire/", {"hourly_rate": "18.00"}, format="json")
    assert again.status_code == 400
    assert Applicant.objects.get(pk=sample["id"]).status == "hired"
    auth(api, "worker.ama@sample.sraj.test")
    tax = api.get("/api/v1/settings/tax/")
    assert tax.status_code == 200
    body = tax.json()["data"]
    assert body["statutory_engine"] == "not_active"
    assert body["net_pay"] is None
    assert all(item["amount"] is None for item in body["items"])

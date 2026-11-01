import pytest

from conftest import bearer
from modules.notifications.models import Notification
from tests.factories import make_address, make_user


@pytest.mark.django_db
def test_users_cannot_read_each_others_addresses(api):
    owner = make_user(email="owner@example.com")
    other = make_user(email="other@example.com")
    address = make_address(owner)
    bearer(api, other)
    hidden = api.get(f"/api/v1/account/addresses/{address.id}/")
    assert hidden.status_code == 404

    bearer(api, owner)
    visible = api.get(f"/api/v1/account/addresses/{address.id}/")
    assert visible.status_code == 200
    created = api.post(
        "/api/v1/account/addresses/",
        {
            "label": "Clinic",
            "recipient_name": "Owner",
            "line1": "4 Ring Road",
            "city": "Accra",
            "region": "Greater Accra",
            "country": "gh",
            "is_default": True,
        },
        format="json",
    )
    assert created.status_code == 201
    assert created.json()["data"]["country"] == "GH"
    assert created.json()["data"]["is_default"] is True
    address.refresh_from_db()
    assert address.is_default is False


@pytest.mark.django_db
def test_users_cannot_mark_another_users_notification_read(api):
    owner = make_user(email="owner@example.com")
    other = make_user(email="other@example.com")
    note = Notification.objects.create(user=owner, title="Private", body="Only the owner can read this.")
    bearer(api, other)
    assert api.patch(f"/api/v1/account/notifications/{note.id}/", {}, format="json").status_code == 404
    bearer(api, owner)
    response = api.patch(f"/api/v1/account/notifications/{note.id}/", {}, format="json")
    assert response.status_code == 200
    assert response.json()["data"]["is_read"] is True

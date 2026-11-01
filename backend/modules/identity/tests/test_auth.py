import pyotp
import pytest
from django.core import mail
from django.test import override_settings
from rest_framework.test import APIClient

from conftest import post_json
from modules.audit.models import AuditLog
from modules.identity.models import PlatformRole, User
from tests.factories import PASSWORD, make_user


@pytest.mark.django_db
def test_me_requires_authentication(api):
    response = api.get("/api/v1/auth/me/")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


@pytest.mark.django_db
def test_browser_login_requires_csrf(db):
    client = APIClient(enforce_csrf_checks=True)
    user = make_user()
    response = client.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": PASSWORD},
        format="json",
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


@pytest.mark.django_db
def test_register_login_and_cookie_session(api, csrf_token):
    created = post_json(
        api,
        "/api/v1/auth/register/",
        {
            "email": "New.User@Example.com",
            "password": PASSWORD,
            "first_name": "Ama",
            "last_name": "Serwaa",
            "platform_role": "platform_admin",
            "is_staff": True,
        },
        csrf_token,
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["user"]["email"] == "new.user@example.com"
    assert body["user"]["platform_role"] == "customer"
    assert body["access"] is None
    assert created.cookies["ms_access"]["httponly"]
    assert "ms_refresh" in created.cookies

    me = api.get("/api/v1/auth/me/")
    assert me.status_code == 200
    assert me.json()["data"]["email_verified"] is False
    assert AuditLog.objects.filter(action="auth.registered").exists()

    logged_out = post_json(api, "/api/v1/auth/logout/", {}, csrf_token)
    assert logged_out.status_code == 200
    assert api.get("/api/v1/auth/me/").status_code == 401

    logged_in = post_json(
        api,
        "/api/v1/auth/login/",
        {"email": "new.user@example.com", "password": PASSWORD},
        csrf_token,
    )
    assert logged_in.status_code == 200
    assert api.get("/api/v1/auth/me/").status_code == 200


@pytest.mark.django_db
def test_register_rejects_a_weak_password(api, csrf_token):
    response = post_json(
        api,
        "/api/v1/auth/register/",
        {
            "email": "weak@example.com",
            "password": "short",
            "first_name": "Ama",
            "last_name": "Serwaa",
        },
        csrf_token,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.django_db
def test_duplicate_email_is_rejected(api, csrf_token, user):
    response = post_json(
        api,
        "/api/v1/auth/register/",
        {
            "email": user.email,
            "password": PASSWORD,
            "first_name": "Ama",
            "last_name": "Serwaa",
        },
        csrf_token,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_unknown_login_does_not_reveal_whether_the_email_exists(api, csrf_token):
    response = post_json(
        api,
        "/api/v1/auth/login/",
        {"email": "missing@example.com", "password": PASSWORD},
        csrf_token,
    )
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Email or password is incorrect."


@pytest.mark.django_db
def test_mobile_login_returns_bearer_tokens_without_csrf(user):
    client = APIClient(enforce_csrf_checks=True)
    response = client.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": PASSWORD},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["access"]
    assert data["refresh"]
    assert "ms_access" not in response.cookies

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")
    me = client.get("/api/v1/auth/me/")
    assert me.status_code == 200

    old_refresh = data["refresh"]
    logged_out = client.post(
        "/api/v1/auth/logout/",
        {"refresh": old_refresh},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert logged_out.status_code == 200
    reused = client.post(
        "/api/v1/auth/refresh/",
        {"refresh": old_refresh},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert reused.status_code == 401


@pytest.mark.django_db
def test_email_verification_and_password_reset_tokens_are_single_use(api, csrf_token):
    post_json(
        api,
        "/api/v1/auth/register/",
        {
            "email": "verify@example.com",
            "password": PASSWORD,
            "first_name": "Ama",
            "last_name": "Serwaa",
        },
        csrf_token,
    )
    verification = _token_from_mail()
    assert post_json(api, "/api/v1/auth/verify-email/", {"token": verification}, csrf_token).status_code == 200
    assert post_json(api, "/api/v1/auth/verify-email/", {"token": verification}, csrf_token).status_code == 400
    assert User.objects.get(email="verify@example.com").email_verified is True

    mail.outbox.clear()
    reset = post_json(api, "/api/v1/auth/password-reset/", {"email": "nobody@example.com"}, csrf_token)
    assert reset.status_code == 200
    assert mail.outbox == []
    post_json(api, "/api/v1/auth/password-reset/", {"email": "verify@example.com"}, csrf_token)
    reset_token = _token_from_mail()
    new_password = "Replacement-Password-9"
    confirmed = post_json(
        api,
        "/api/v1/auth/password-reset/confirm/",
        {"token": reset_token, "password": new_password},
        csrf_token,
    )
    assert confirmed.status_code == 200
    assert post_json(
        api,
        "/api/v1/auth/login/",
        {"email": "verify@example.com", "password": new_password},
        csrf_token,
    ).status_code == 200


@pytest.mark.django_db
@override_settings(MFA_REQUIRED_FOR_PRIVILEGED=True)
def test_privileged_account_must_enroll_mfa_before_it_receives_a_session():
    client = APIClient(enforce_csrf_checks=True)
    make_user(email="admin@example.com", platform_role=PlatformRole.PLATFORM_ADMIN)
    blocked = client.post(
        "/api/v1/auth/login/",
        {"email": "admin@example.com", "password": PASSWORD},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "mfa_enrollment_required"
    enrollment = blocked.json()["error"]["details"]["enrollment_token"]

    enrolled = client.post(
        "/api/v1/auth/mfa/enroll/",
        {"enrollment_token": enrollment},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert enrolled.status_code == 200
    secret = enrolled.json()["data"]["secret"]
    confirmed = client.post(
        "/api/v1/auth/mfa/confirm/",
        {"enrollment_token": enrollment, "code": pyotp.TOTP(secret).now()},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert confirmed.status_code == 200

    challenged = client.post(
        "/api/v1/auth/login/",
        {"email": "admin@example.com", "password": PASSWORD},
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert challenged.status_code == 200
    assert challenged.json()["data"]["mfa_required"] is True
    assert challenged.json()["data"]["access"] is None

    verified = client.post(
        "/api/v1/auth/mfa/verify/",
        {
            "mfa_token": challenged.json()["data"]["mfa_token"],
            "code": pyotp.TOTP(secret).now(),
        },
        format="json",
        HTTP_X_CLIENT="mobile",
    )
    assert verified.status_code == 200
    assert verified.json()["data"]["access"]


def _token_from_mail() -> str:
    body = mail.outbox[-1].body
    return body.split("token=")[1].split()[0].strip()

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import PASSWORD, make_user


@pytest.fixture
def api():
    return APIClient(enforce_csrf_checks=True, HTTP_ORIGIN="http://testserver")


@pytest.fixture
def csrf_token(api):
    response = api.get("/api/v1/auth/csrf/")
    assert response.status_code == 200
    return response.json()["data"]["csrf_token"]


@pytest.fixture
def user(db):
    return make_user()


def bearer(api, user):
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


def post_json(api, path, payload, csrf_token, **headers):
    return api.post(path, payload, format="json", HTTP_X_CSRFTOKEN=csrf_token, **headers)

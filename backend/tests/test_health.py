import pytest

from common.tasks import ping


@pytest.mark.django_db
def test_health_ok(api):
    response = api.get("/api/v1/health/")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"


@pytest.mark.django_db
def test_health_reports_database_failure(api, monkeypatch):
    monkeypatch.setattr("common.health.database_status", lambda: "error")
    response = api.get("/api/v1/health/")
    assert response.status_code == 503
    assert response.json()["data"]["status"] == "degraded"


@pytest.mark.django_db
def test_api_root(api):
    response = api.get("/")
    assert response.status_code == 200
    assert response.json()["data"]["service"] == "medisource-api"


@pytest.mark.django_db
def test_schema_mentions_the_api(api):
    response = api.get("/api/schema/")
    assert response.status_code == 200
    assert b"MediSource GH API" in response.content


@pytest.mark.django_db
def test_celery_ping_runs_eagerly():
    from config.celery import app

    assert app.main == "medisource"
    ping.app.conf.task_always_eager = True
    ping.app.conf.task_eager_propagates = True
    assert ping.apply().get(timeout=10) == "pong"

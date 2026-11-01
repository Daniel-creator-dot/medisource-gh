from django.db import connection
from django.db.utils import OperationalError
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import ok


def database_status() -> str:
    try:
        connection.ensure_connection()
        return "ok"
    except OperationalError:
        return "error"


def redis_status() -> str:
    from django.conf import settings

    if not settings.REDIS_URL:
        return "not_configured"
    try:
        import redis

        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
        client.ping()
        return "ok"
    except Exception:
        return "error"


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        checks = {"database": database_status(), "redis": redis_status()}
        healthy = checks["database"] == "ok" and checks["redis"] in {"ok", "not_configured"}
        return ok(
            {
                "status": "ok" if healthy else "degraded",
                "service": "medisource-api",
                "checks": checks,
            },
            status=200 if healthy else 503,
        )


class ApiRootView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return ok({"service": "medisource-api", "docs": "/api/docs/", "health": "/api/v1/health/"})

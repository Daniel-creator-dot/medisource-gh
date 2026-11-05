from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import ok


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        database = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            database = "error"
        return ok(
            {
                "status": "ok" if database == "ok" else "degraded",
                "service": "sraj-nova-api",
                "checks": {"database": database},
            }
        )

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import ok
from modules.finance.services import finance_summary, rebuild_week_invoices
from modules.identity.models import AGENCY_ROLES, AgencyRole


class FinanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        return ok(finance_summary(request.user))


class RebuildInvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in AGENCY_ROLES:
            raise PermissionDenied()
        rebuild_week_invoices()
        return ok(finance_summary(request.user))

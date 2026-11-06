from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.finance.ledger import BooksError, books_snapshot, post_week_invoices, record_receipt
from modules.finance.models import ClientInvoice
from modules.finance.services import finance_summary, money, rebuild_week_invoices
from modules.identity.models import AGENCY_ROLES, AgencyRole


def _agency(user):
    if user.role not in AGENCY_ROLES:
        raise PermissionDenied()


class FinanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        return ok(finance_summary(request.user))


class RebuildInvoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _agency(request.user)
        rebuild_week_invoices()
        return ok(finance_summary(request.user))


class BooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _agency(request.user)
        return ok(books_snapshot())


class PostWeekView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _agency(request.user)
        try:
            count = post_week_invoices()
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        payload = books_snapshot()
        payload["posted_invoices"] = count
        return ok(payload)


class ReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _agency(request.user)
        invoice = ClientInvoice.objects.filter(pk=request.data.get("invoice_id")).first()
        if invoice is None:
            raise NotFound()
        try:
            amount = money(request.data.get("amount"))
        except Exception:
            return error_response("amount_invalid", "Enter a receipt amount.", 400)
        try:
            record_receipt(
                invoice=invoice,
                amount=amount,
                reference=str(request.data.get("reference") or ""),
                received_on=timezone.localdate(),
            )
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(books_snapshot(), status=201)


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

from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.finance.ledger import (
    BooksError,
    books_snapshot,
    ledger_position,
    post_draft,
    post_week_invoices,
    record_receipt,
    reverse_entry,
    save_manual_draft,
    set_period_status,
)
from modules.finance.models import AccountingPeriod, ClientInvoice, JournalEntry
from modules.finance.services import finance_summary, money, rebuild_week_invoices
from modules.identity.models import AGENCY_ROLES, AgencyRole


def _agency(user):
    if user.role not in AGENCY_ROLES:
        raise PermissionDenied()


class TaxSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok(
            {
                "statutory_engine": "not_active",
                "net_pay": None,
                "items": [
                    {"name": "PAYE", "status": "not_configured", "amount": None},
                    {"name": "SSNIT", "status": "not_configured", "amount": None},
                    {"name": "Tier 2 pension", "status": "not_configured", "amount": None},
                ],
                "note": "No Ghana tax or pension rate is stored. Net pay is not calculated.",
            }
        )


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


class LedgerPositionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _agency(request.user)
        return ok(ledger_position())


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


class ManualJournalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _agency(request.user)
        entry_date = parse_date(str(request.data.get("entry_date") or ""))
        if entry_date is None:
            return error_response("invalid_journal", "Enter a posting date.", 400)
        try:
            entry = save_manual_draft(entry_date=entry_date, memo=str(request.data.get("memo") or ""), lines=request.data.get("lines") or [])
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok({"id": str(entry.id), "status": entry.status}, status=201)


class PostDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entry_id):
        _agency(request.user)
        entry = JournalEntry.objects.filter(pk=entry_id).first()
        if entry is None:
            raise NotFound()
        try:
            post_draft(entry)
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(books_snapshot())


class ReverseJournalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entry_id):
        _agency(request.user)
        entry = JournalEntry.objects.filter(pk=entry_id).first()
        if entry is None:
            raise NotFound()
        try:
            reverse_entry(entry)
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(books_snapshot())


class PeriodStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, period_id):
        _agency(request.user)
        period = AccountingPeriod.objects.filter(pk=period_id).first()
        if period is None:
            raise NotFound()
        try:
            set_period_status(period, str(request.data.get("status") or ""))
        except BooksError as exc:
            return error_response(exc.code, exc.message, 400)
        return ok(books_snapshot())

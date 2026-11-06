from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from modules.finance.models import Account, ClientInvoice, ClientReceipt, JournalEntry, JournalLine
from modules.finance.services import money, money_str

CHART = (
    ("1000", "Cash", "asset"),
    ("1100", "Accounts receivable", "asset"),
    ("2000", "Wages payable", "liability"),
    ("3000", "Opening equity", "equity"),
    ("4000", "Agency fee revenue", "income"),
)
OPENING_MEMO = "Sample opening cash balance"


class BooksError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def ensure_chart() -> None:
    for code, name, account_type in CHART:
        Account.objects.get_or_create(code=code, defaults={"name": name, "account_type": account_type, "is_demo": True})


def _account(code: str) -> Account:
    ensure_chart()
    return Account.objects.get(code=code)


def _open_entries(invoice: ClientInvoice):
    reversed_ids = JournalEntry.objects.filter(reverses__isnull=False).values("reverses_id")
    return invoice.journals.filter(reverses__isnull=True).exclude(id__in=reversed_ids)


def invoice_has_open_journal(invoice: ClientInvoice) -> bool:
    return _open_entries(invoice).exists()


def invoice_outstanding(invoice: ClientInvoice) -> Decimal:
    paid = invoice.receipts.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return money(invoice.total - paid)


def cash_balance():
    account = Account.objects.filter(code="1000").first()
    if account is None or not account.lines.exists():
        return None
    totals = account.lines.aggregate(debit=Sum("debit"), credit=Sum("credit"))
    return money((totals["debit"] or Decimal("0.00")) - (totals["credit"] or Decimal("0.00")))


@transaction.atomic
def _save_entry(*, entry_date, memo: str, lines: list[dict], invoice=None, reverses=None) -> JournalEntry:
    debits = sum((money(row["debit"]) for row in lines), Decimal("0.00"))
    credits = sum((money(row["credit"]) for row in lines), Decimal("0.00"))
    if debits != credits or debits <= 0:
        raise BooksError("unbalanced", "The journal does not balance.")
    entry = JournalEntry.objects.create(
        entry_date=entry_date,
        memo=memo,
        invoice=invoice,
        reverses=reverses,
        is_demo=True,
    )
    for row in lines:
        JournalLine.objects.create(
            entry=entry,
            account=_account(row["code"]),
            debit=money(row["debit"]),
            credit=money(row["credit"]),
        )
    return entry


def post_opening_cash(amount, occurred_on) -> None:
    ensure_chart()
    if JournalEntry.objects.filter(memo=OPENING_MEMO).exists():
        return
    if money(amount) <= 0:
        return
    _save_entry(
        entry_date=occurred_on,
        memo=OPENING_MEMO,
        lines=[
            {"code": "1000", "debit": amount, "credit": 0},
            {"code": "3000", "debit": 0, "credit": amount},
        ],
    )


def _reverse(entry: JournalEntry) -> JournalEntry:
    return _save_entry(
        entry_date=timezone.localdate(),
        memo=f"Reversal of {entry.memo}",
        invoice=entry.invoice,
        reverses=entry,
        lines=[{"code": line.account.code, "debit": line.credit, "credit": line.debit} for line in entry.lines.select_related("account")],
    )


@transaction.atomic
def post_week_invoices(day=None) -> int:
    from modules.finance.services import week_start

    ensure_chart()
    start = week_start(day)
    posted = 0
    for invoice in ClientInvoice.objects.filter(week_start=start).select_related("client"):
        for entry in list(_open_entries(invoice)):
            _reverse(entry)
        if invoice.total <= 0:
            continue
        lines = [{"code": "1100", "debit": invoice.total, "credit": 0}]
        if invoice.employment_cost > 0:
            lines.append({"code": "2000", "debit": 0, "credit": invoice.employment_cost})
        if invoice.agency_fee > 0:
            lines.append({"code": "4000", "debit": 0, "credit": invoice.agency_fee})
        _save_entry(
            entry_date=timezone.localdate(),
            memo=f"Invoice {invoice.client.legal_name} week {start.isoformat()}",
            invoice=invoice,
            lines=lines,
        )
        posted += 1
    return posted


@transaction.atomic
def record_receipt(*, invoice: ClientInvoice, amount, reference: str, received_on) -> ClientReceipt:
    reference = reference.strip()
    if not reference:
        raise BooksError("reference_required", "A receipt reference is required.")
    if ClientReceipt.objects.filter(reference=reference).exists():
        raise BooksError("duplicate_reference", "That receipt reference is already recorded.")
    if not invoice_has_open_journal(invoice):
        raise BooksError("invoice_not_posted", "Post the invoice to the ledger before recording a receipt.")
    amount = money(amount)
    outstanding = invoice_outstanding(invoice)
    if amount <= 0 or amount > outstanding:
        raise BooksError("amount_invalid", "The receipt must be greater than zero and no more than the outstanding invoice.")
    entry = _save_entry(
        entry_date=received_on,
        memo=f"Receipt {reference}",
        invoice=invoice,
        lines=[
            {"code": "1000", "debit": amount, "credit": 0},
            {"code": "1100", "debit": 0, "credit": amount},
        ],
    )
    return ClientReceipt.objects.create(
        client=invoice.client,
        invoice=invoice,
        journal=entry,
        received_on=received_on,
        amount=amount,
        reference=reference,
        is_demo=True,
    )


def trial_balance() -> dict:
    ensure_chart()
    rows = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    for account in Account.objects.order_by("code"):
        totals = account.lines.aggregate(debit=Sum("debit"), credit=Sum("credit"))
        debit = money(totals["debit"] or 0)
        credit = money(totals["credit"] or 0)
        total_debit += debit
        total_credit += credit
        rows.append(
            {
                "code": account.code,
                "name": account.name,
                "account_type": account.account_type,
                "debit": money_str(debit),
                "credit": money_str(credit),
            }
        )
    return {
        "rows": rows,
        "total_debit": money_str(total_debit),
        "total_credit": money_str(total_credit),
        "balanced": total_debit == total_credit,
    }


def aging_rows(invoices) -> list[dict]:
    today = timezone.localdate()
    rows = []
    for invoice in invoices:
        outstanding = invoice_outstanding(invoice)
        if outstanding <= 0:
            continue
        age = (today - invoice.week_start).days
        if age <= 7:
            bucket = "current"
        elif age <= 30:
            bucket = "8 to 30 days"
        else:
            bucket = "over 30 days"
        rows.append(
            {
                "invoice_id": str(invoice.id),
                "client_name": invoice.client.legal_name,
                "week_start": invoice.week_start.isoformat(),
                "outstanding": money_str(outstanding),
                "bucket": bucket,
            }
        )
    return rows


def books_snapshot() -> dict:
    ensure_chart()
    journals = []
    for entry in JournalEntry.objects.prefetch_related("lines__account").order_by("created_at"):
        journals.append(
            {
                "id": str(entry.id),
                "entry_date": entry.entry_date.isoformat(),
                "memo": entry.memo,
                "reversal": entry.reverses_id is not None,
                "lines": [
                    {
                        "code": line.account.code,
                        "name": line.account.name,
                        "debit": money_str(line.debit),
                        "credit": money_str(line.credit),
                    }
                    for line in entry.lines.all()
                ],
            }
        )
    invoices = ClientInvoice.objects.select_related("client").order_by("client__legal_name")
    return {
        "accounts": [
            {"code": account.code, "name": account.name, "account_type": account.account_type}
            for account in Account.objects.order_by("code")
        ],
        "journals": journals,
        "trial_balance": trial_balance(),
        "aging": aging_rows(invoices),
        "open_invoices": [
            {
                "id": str(invoice.id),
                "client_name": invoice.client.legal_name,
                "outstanding": money_str(invoice_outstanding(invoice)),
                "posted": invoice_has_open_journal(invoice),
            }
            for invoice in invoices
            if invoice_outstanding(invoice) > 0
        ],
        "receipts": [
            {
                "reference": receipt.reference,
                "client_name": receipt.client.legal_name,
                "amount": money_str(receipt.amount),
                "received_on": receipt.received_on.isoformat(),
            }
            for receipt in ClientReceipt.objects.select_related("client").order_by("-received_on")
        ],
        "note": "Receipts and journals are demonstration book entries. They are not a bank or mobile-money settlement.",
    }

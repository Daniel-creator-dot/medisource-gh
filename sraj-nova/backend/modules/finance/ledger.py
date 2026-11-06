from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from modules.finance.models import (
    Account,
    AccountGroup,
    AccountingPeriod,
    ClientInvoice,
    ClientReceipt,
    FiscalYear,
    JournalEntry,
    JournalLine,
    JournalStatus,
)
from modules.finance.services import money, money_str

CHART = (
    ("1000", "Cash", "asset"),
    ("1100", "Accounts receivable", "asset"),
    ("2000", "Wages payable", "liability"),
    ("3000", "Opening equity", "equity"),
    ("4000", "Agency fee revenue", "income"),
)
GROUPS = (
    ("AS", "Assets", "asset"),
    ("LI", "Liabilities", "liability"),
    ("EQ", "Equity", "equity"),
    ("IN", "Income", "income"),
)
OPENING_MEMO = "Sample opening cash balance"


class BooksError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def ensure_chart() -> None:
    groups = {}
    for code, name, account_type in GROUPS:
        group, _created = AccountGroup.objects.get_or_create(code=code, defaults={"name": name, "account_type": account_type})
        groups[account_type] = group
    for code, name, account_type in CHART:
        account, _created = Account.objects.get_or_create(
            code=code, defaults={"name": name, "account_type": account_type, "is_demo": True}
        )
        if account.group_id is None:
            account.group = groups[account_type]
            account.save(update_fields=["group", "updated_at"])
    ensure_periods()


def ensure_periods(day=None):
    day = day or timezone.localdate()
    start = day.replace(month=1, day=1)
    end = day.replace(month=12, day=31)
    fiscal, _created = FiscalYear.objects.get_or_create(
        starts_on=start, defaults={"ends_on": end, "label": str(day.year), "status": "open"}
    )
    period, _created = AccountingPeriod.objects.get_or_create(
        fiscal_year=fiscal,
        starts_on=start,
        defaults={"ends_on": end, "name": str(day.year), "status": fiscal.status},
    )
    JournalEntry.objects.filter(period__isnull=True, entry_date__gte=period.starts_on, entry_date__lte=period.ends_on).update(period=period)
    return period


def period_for(day):
    ensure_periods(day)
    period = AccountingPeriod.objects.filter(starts_on__lte=day, ends_on__gte=day).first()
    if period is None:
        raise BooksError("period_missing", "No accounting period covers that date.")
    if period.status != "open":
        raise BooksError("period_closed", "That accounting period is closed.")
    return period


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
    posted = account.lines.filter(entry__status=JournalStatus.POSTED) if account is not None else JournalLine.objects.none()
    if account is None or not posted.exists():
        return None
    totals = posted.aggregate(debit=Sum("debit"), credit=Sum("credit"))
    return money((totals["debit"] or Decimal("0.00")) - (totals["credit"] or Decimal("0.00")))


@transaction.atomic
def _save_entry(*, entry_date, memo: str, lines: list[dict], invoice=None, reverses=None) -> JournalEntry:
    debits = sum((money(row["debit"]) for row in lines), Decimal("0.00"))
    credits = sum((money(row["credit"]) for row in lines), Decimal("0.00"))
    if debits != credits or debits <= 0:
        raise BooksError("unbalanced", "The journal does not balance.")
    period = period_for(entry_date)
    entry = JournalEntry.objects.create(
        entry_date=entry_date,
        memo=memo,
        invoice=invoice,
        reverses=reverses,
        period=period,
        status=JournalStatus.POSTED,
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


def _parse_lines(lines) -> list[dict]:
    if not isinstance(lines, list) or not lines:
        raise BooksError("lines_required", "Add at least one journal line.")
    parsed = []
    for row in lines:
        if not isinstance(row, dict):
            raise BooksError("invalid_line", "Each journal line needs an account and an amount.")
        try:
            debit = money(row.get("debit") or 0)
            credit = money(row.get("credit") or 0)
        except Exception as exc:
            raise BooksError("invalid_line", "Enter a debit or a credit amount.") from exc
        if (debit > 0 and credit > 0) or (debit == 0 and credit == 0):
            raise BooksError("invalid_line", "Each line needs a debit or a credit, not both.")
        code = str(row.get("code") or "").strip()
        if not Account.objects.filter(code=code).exists():
            raise BooksError("unknown_account", "Choose an account from the chart.")
        parsed.append({"code": code, "debit": debit, "credit": credit})
    return parsed


@transaction.atomic
def save_manual_draft(*, entry_date, memo: str, lines) -> JournalEntry:
    ensure_chart()
    memo = memo.strip()
    if not memo:
        raise BooksError("memo_required", "A memo is required.")
    parsed = _parse_lines(lines)
    entry = JournalEntry.objects.create(entry_date=entry_date, memo=memo, status=JournalStatus.DRAFT, is_demo=False)
    for row in parsed:
        JournalLine.objects.create(entry=entry, account=_account(row["code"]), debit=row["debit"], credit=row["credit"])
    return entry


@transaction.atomic
def post_draft(entry: JournalEntry) -> JournalEntry:
    if entry.status != JournalStatus.DRAFT:
        raise BooksError("already_posted", "This journal is already posted.")
    rows = list(entry.lines.all())
    debits = sum((money(row.debit) for row in rows), Decimal("0.00"))
    credits = sum((money(row.credit) for row in rows), Decimal("0.00"))
    if debits != credits or debits <= 0:
        raise BooksError("unbalanced", "The journal does not balance.")
    entry.period = period_for(entry.entry_date)
    entry.status = JournalStatus.POSTED
    entry.save(update_fields=["period", "status", "updated_at"])
    return entry


@transaction.atomic
def reverse_entry(entry: JournalEntry) -> JournalEntry:
    if entry.status != JournalStatus.POSTED:
        raise BooksError("not_posted", "Only a posted journal can be reversed.")
    if entry.reversals.exists():
        raise BooksError("already_reversed", "This journal already has a reversal.")
    return _reverse(entry)


def set_period_status(period: AccountingPeriod, status: str) -> AccountingPeriod:
    if status not in {"open", "closed"}:
        raise BooksError("invalid_period", "A period is open or closed.")
    period.status = status
    period.save(update_fields=["status", "updated_at"])
    return period


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
        totals = account.lines.filter(entry__status=JournalStatus.POSTED).aggregate(debit=Sum("debit"), credit=Sum("credit"))
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


def ledger_position() -> dict:
    """Classify posted lines. Fee revenue is not reported as profit."""
    sheet = trial_balance()
    sections: dict[str, list[dict]] = {"asset": [], "liability": [], "equity": [], "income": [], "expense": []}
    totals = {key: Decimal("0.00") for key in sections}
    for row in sheet["rows"]:
        debit = money(row["debit"])
        credit = money(row["credit"])
        kind = row["account_type"] if row["account_type"] in sections else "expense"
        balance = money(credit - debit) if kind in {"liability", "equity", "income"} else money(debit - credit)
        sections[kind].append({"code": row["code"], "name": row["name"], "balance": money_str(balance)})
        totals[kind] += balance
    fee = next((row["balance"] for row in sections["income"] if row["code"] == "4000"), "0.00")
    return {
        "basis": (
            "Posted journal lines only. Employment cost is held as wages payable, not as an expense. "
            "PAYE, pension, and net pay are not posted."
        ),
        "sections": sections,
        "assets": money_str(totals["asset"]),
        "liabilities": money_str(totals["liability"]),
        "equity": money_str(totals["equity"]),
        "income": money_str(totals["income"]),
        "expenses": money_str(totals["expense"]),
        "recognized_fee_revenue": fee,
        "operating_profit": None,
        "operating_profit_reason": "No expense account has been posted, so fee revenue is not operating profit.",
        "trial_balance_balanced": sheet["balanced"],
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
                "status": entry.status,
                "reversal": entry.reverses_id is not None,
                "reversed": entry.reversals.exists(),
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
            {
                "code": account.code,
                "name": account.name,
                "account_type": account.account_type,
                "group": account.group.name if account.group_id else None,
            }
            for account in Account.objects.select_related("group").order_by("code")
        ],
        "periods": [
            {
                "id": str(period.id),
                "name": period.name,
                "starts_on": period.starts_on.isoformat(),
                "ends_on": period.ends_on.isoformat(),
                "status": period.status,
            }
            for period in AccountingPeriod.objects.order_by("starts_on")
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

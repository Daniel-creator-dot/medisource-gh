from decimal import Decimal

from django.db import models

from common.models import UUIDModel


class CashMovement(UUIDModel):
    occurred_on = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=240, unique=True)
    is_demo = models.BooleanField(default=False)


class ClientInvoice(UUIDModel):
    client = models.ForeignKey("organization.Client", on_delete=models.PROTECT, related_name="invoices")
    week_start = models.DateField()
    employment_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    agency_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="GHS")
    status = models.CharField(max_length=16, default="issued")
    is_demo = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["client", "week_start"], name="one_invoice_per_client_week")]

    @property
    def total(self) -> Decimal:
        return self.employment_cost + self.agency_fee


class AccountGroup(UUIDModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=120)
    account_type = models.CharField(max_length=16)


class Account(UUIDModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=120)
    account_type = models.CharField(max_length=16)
    group = models.ForeignKey(AccountGroup, null=True, blank=True, on_delete=models.PROTECT, related_name="accounts")
    is_demo = models.BooleanField(default=True)


class FiscalYear(UUIDModel):
    label = models.CharField(max_length=16)
    starts_on = models.DateField(unique=True)
    ends_on = models.DateField()
    status = models.CharField(max_length=16, default="open")


class AccountingPeriod(UUIDModel):
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name="periods")
    name = models.CharField(max_length=32)
    starts_on = models.DateField()
    ends_on = models.DateField()
    status = models.CharField(max_length=16, default="open")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["fiscal_year", "starts_on"], name="one_period_start_per_year")]


class JournalStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    POSTED = "posted", "Posted"


class JournalEntry(UUIDModel):
    entry_date = models.DateField()
    memo = models.CharField(max_length=240)
    invoice = models.ForeignKey(ClientInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="journals")
    reverses = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="reversals")
    period = models.ForeignKey(AccountingPeriod, null=True, blank=True, on_delete=models.PROTECT, related_name="journals")
    status = models.CharField(max_length=16, choices=JournalStatus.choices, default=JournalStatus.POSTED)
    is_demo = models.BooleanField(default=False)


class JournalLine(UUIDModel):
    entry = models.ForeignKey(JournalEntry, on_delete=models.PROTECT, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="lines")
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(debit__gte=0) & models.Q(credit__gte=0),
                name="journal_line_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(debit__gt=0, credit=0) | models.Q(credit__gt=0, debit=0),
                name="journal_line_one_sided",
            ),
        ]


class ClientReceipt(UUIDModel):
    client = models.ForeignKey("organization.Client", on_delete=models.PROTECT, related_name="receipts")
    invoice = models.ForeignKey(ClientInvoice, on_delete=models.PROTECT, related_name="receipts")
    journal = models.OneToOneField(JournalEntry, on_delete=models.PROTECT, related_name="receipt")
    received_on = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=80, unique=True)
    is_demo = models.BooleanField(default=False)

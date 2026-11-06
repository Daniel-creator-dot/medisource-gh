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


class Account(UUIDModel):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=120)
    account_type = models.CharField(max_length=16)
    is_demo = models.BooleanField(default=True)


class JournalEntry(UUIDModel):
    entry_date = models.DateField()
    memo = models.CharField(max_length=240)
    invoice = models.ForeignKey(ClientInvoice, null=True, blank=True, on_delete=models.PROTECT, related_name="journals")
    reverses = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="reversals")
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

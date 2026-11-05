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

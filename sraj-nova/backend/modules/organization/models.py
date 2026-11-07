from decimal import Decimal

from django.db import models

from common.models import UUIDModel


class Agency(UUIDModel):
    legal_name = models.CharField(max_length=200)
    trading_name = models.CharField(max_length=200)
    country = models.CharField(max_length=2, default="GH")
    currency = models.CharField(max_length=3, default="GHS")
    timezone = models.CharField(max_length=64, default="Africa/Accra")
    seeded_on = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.trading_name


class ClientStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class Client(UUIDModel):
    legal_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    sector = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=ClientStatus.choices, default=ClientStatus.ACTIVE)
    is_demo = models.BooleanField(default=False)
    demo_label = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["legal_name"]

    def __str__(self) -> str:
        return self.legal_name


class ClientSite(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="sites")
    name = models.CharField(max_length=160)
    city = models.CharField(max_length=80)
    region = models.CharField(max_length=80)
    is_demo = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Department(UUIDModel):
    site = models.ForeignKey(ClientSite, on_delete=models.PROTECT, related_name="departments")
    name = models.CharField(max_length=160)

    def __str__(self) -> str:
        return self.name


class JobPosition(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="positions")
    title = models.CharField(max_length=160)
    required_skill = models.CharField(max_length=80, blank=True)

    def __str__(self) -> str:
        return self.title


class BillingModel(models.TextChoices):
    COST_PLUS = "cost_plus", "Cost plus"
    FIXED_FEE = "fixed_fee", "Fixed fee"
    HOURLY = "hourly", "Hourly"
    PER_WORKER = "per_worker", "Per worker"
    HYBRID = "hybrid", "Hybrid"


class ServiceContract(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="contracts")
    title = models.CharField(max_length=200)
    billing_model = models.CharField(max_length=32, choices=BillingModel.choices, default=BillingModel.COST_PLUS)
    management_fee_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.1200"))
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_demo = models.BooleanField(default=False)

    class Meta:
        ordering = ["ends_on"]

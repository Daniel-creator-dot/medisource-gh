from django.db import models

from common.models import UUIDTimeStampedModel
from modules.organizations.models import Organization


class Category(UUIDTimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class CategoryPolicy(UUIDTimeStampedModel):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name="policy")
    checkout_enabled = models.BooleanField(default=False)
    requires_authorization = models.BooleanField(default=False)
    policy_reference = models.CharField(max_length=300)

    def __str__(self) -> str:
        return f"Policy for {self.category.name}"


class MasterProduct(UUIDTimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    manufacturer = models.CharField(max_length=160)
    brand = models.CharField(max_length=160)
    generic_name = models.CharField(max_length=160, blank=True)
    description = models.TextField()
    specification = models.TextField()
    strength = models.CharField(max_length=80, blank=True)
    dosage_form = models.CharField(max_length=80, blank=True)
    pack_size = models.CharField(max_length=80)
    unit_of_measure = models.CharField(max_length=40)
    gtin = models.CharField(max_length=32, blank=True)
    regulatory_notes = models.TextField(blank=True)
    is_demo = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class SupplierVerification(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_REVIEW = "in_review", "In review"
    VERIFIED = "verified", "Verified"
    REJECTED = "rejected", "Rejected"
    SUSPENDED = "suspended", "Suspended"
    DEMO = "demo", "Sample record"


class Supplier(UUIDTimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.PROTECT, related_name="supplier_profile")
    display_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    summary = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=32,
        choices=SupplierVerification.choices,
        default=SupplierVerification.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_demo = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


class ListingStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class Listing(UUIDTimeStampedModel):
    master_product = models.ForeignKey(MasterProduct, on_delete=models.PROTECT, related_name="listings")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="listings")
    sku = models.CharField(max_length=64)
    price_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="GHS")
    stock_quantity = models.PositiveIntegerField()
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    lead_time_days = models.PositiveIntegerField(default=0)
    warehouse_name = models.CharField(max_length=160)
    delivery_zones = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=ListingStatus.choices, default=ListingStatus.DRAFT)
    is_demo = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["supplier", "sku"], name="unique_supplier_sku"),
            models.CheckConstraint(condition=models.Q(price_amount__gte=0), name="listing_price_nonnegative"),
            models.CheckConstraint(condition=models.Q(stock_quantity__gte=0), name="listing_stock_nonnegative"),
            models.CheckConstraint(condition=models.Q(minimum_order_quantity__gte=1), name="listing_moq_positive"),
            models.CheckConstraint(condition=models.Q(lead_time_days__gte=0), name="listing_lead_time_nonnegative"),
        ]

    def __str__(self) -> str:
        return f"{self.sku} ({self.supplier.display_name})"

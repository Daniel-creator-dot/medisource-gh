from decimal import Decimal

from modules.catalog.models import (
    Category,
    CategoryPolicy,
    Listing,
    ListingStatus,
    MasterProduct,
    Supplier,
    SupplierVerification,
)
from modules.identity.models import Address, PlatformRole, User
from modules.organizations.models import MembershipRole, OrganizationType
from modules.organizations.services import create_organization

PASSWORD = "Medisource-Test-User-1"


def make_user(*, email="user@example.com", password=PASSWORD, **extra) -> User:
    return User.objects.create_user(email=email, password=password, **extra)


def make_category(*, slug="ppe", name="PPE", checkout=True, requires=False) -> Category:
    category = Category.objects.create(name=name, slug=slug, description=f"{name} test category.")
    CategoryPolicy.objects.create(
        category=category,
        checkout_enabled=checkout,
        requires_authorization=requires,
        policy_reference="Test policy. Not a regulatory approval.",
    )
    return category


def make_supplier(
    *,
    owner,
    slug="sample-supplier",
    status=SupplierVerification.DEMO,
    is_demo=True,
    org_status="active",
):
    organization = create_organization(
        name=slug,
        slug=f"{slug}-org",
        org_type=OrganizationType.SUPPLIER,
        owner=owner,
        role=MembershipRole.OWNER,
    )
    if org_status != "active":
        organization.status = org_status
        organization.save(update_fields=["status"])
    return Supplier.objects.create(
        organization=organization,
        display_name=slug,
        slug=slug,
        summary="Test supplier",
        city="Accra",
        region="Greater Accra",
        verification_status=status,
        is_demo=is_demo,
        internal_notes="Private note that other suppliers must not see.",
    )


def make_product(*, category, slug="nitrile-gloves", name="Nitrile gloves", is_demo=True) -> MasterProduct:
    return MasterProduct.objects.create(
        category=category,
        name=name,
        slug=slug,
        manufacturer="SampleMed Industries",
        brand="SampleMed",
        description="A test product description for search.",
        specification="Test specification.",
        pack_size="Box of 100",
        unit_of_measure="box",
        is_demo=is_demo,
    )


def make_listing(*, product, supplier, sku="SKU-1", price="10.00", stock=20, moq=1, status=ListingStatus.ACTIVE, is_demo=True):
    return Listing.objects.create(
        master_product=product,
        supplier=supplier,
        sku=sku,
        price_amount=Decimal(price),
        stock_quantity=stock,
        minimum_order_quantity=moq,
        lead_time_days=2,
        warehouse_name="Test warehouse",
        delivery_zones=["Greater Accra"],
        status=status,
        is_demo=is_demo,
    )


def make_address(user, **extra) -> Address:
    payload = {
        "label": "Home",
        "recipient_name": "Test User",
        "line1": "12 Independence Avenue",
        "city": "Accra",
        "region": "Greater Accra",
        "country": "GH",
        "is_default": True,
    }
    payload.update(extra)
    return Address.objects.create(user=user, **payload)

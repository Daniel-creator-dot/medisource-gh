import pytest
from django.core.management import call_command
from django.test import override_settings

from conftest import bearer
from modules.catalog.models import CategoryPolicy, ListingStatus, SupplierVerification
from modules.catalog.services import purchase_block_reason
from modules.identity.models import PlatformRole
from tests.factories import make_category, make_listing, make_product, make_supplier, make_user


@pytest.mark.django_db
def test_public_catalogue_hides_pending_suppliers_and_private_notes(api):
    owner = make_user(email="owner@example.com")
    pending_owner = make_user(email="pending@example.com")
    stranger = make_user(email="stranger@example.com")
    category = make_category()
    demo = make_supplier(owner=owner, slug="sample-harbour")
    pending = make_supplier(
        owner=pending_owner,
        slug="pending-house",
        status=SupplierVerification.PENDING,
        is_demo=False,
    )
    product = make_product(category=category, slug="gloves")
    make_listing(product=product, supplier=demo, sku="PUBLIC")
    hidden_product = make_product(category=category, slug="hidden-item", name="Hidden item")
    make_listing(product=hidden_product, supplier=pending, sku="SECRET", is_demo=False)

    listed = api.get("/api/v1/catalog/products/")
    slugs = [item["slug"] for item in listed.json()["data"]]
    assert slugs == ["gloves"]
    assert "Private note" not in listed.content.decode()

    detail = api.get("/api/v1/catalog/suppliers/sample-harbour/")
    assert detail.status_code == 200
    assert "internal_notes" not in detail.json()["data"]
    assert api.get("/api/v1/catalog/suppliers/pending-house/").status_code == 404
    assert api.get("/api/v1/catalog/products/hidden-item/").status_code == 404

    bearer(api, stranger)
    assert api.get("/api/v1/catalog/suppliers/sample-harbour/internal/").status_code == 404
    admin = make_user(email="admin@example.com", platform_role=PlatformRole.PLATFORM_ADMIN)
    bearer(api, admin)
    assert api.get("/api/v1/catalog/suppliers/sample-harbour/internal/").status_code == 404
    bearer(api, owner)
    notes = api.get("/api/v1/catalog/suppliers/sample-harbour/internal/")
    assert notes.status_code == 200
    assert "Private note" in notes.json()["data"]["internal_notes"]


@pytest.mark.django_db
def test_demo_and_closed_categories_cannot_be_purchased():
    owner = make_user()
    consumable = make_category(slug="consumable", checkout=True)
    medicine = make_category(slug="authorized-pharmaceuticals", name="Medicines", checkout=False, requires=True)
    demo_supplier = make_supplier(owner=owner, slug="demo-supplier")
    verified_owner = make_user(email="verified@example.com")
    verified = make_supplier(
        owner=verified_owner,
        slug="verified-supplier",
        status=SupplierVerification.VERIFIED,
        is_demo=False,
    )
    demo_listing = make_listing(
        product=make_product(category=consumable, slug="demo-gloves"),
        supplier=demo_supplier,
    )
    real_listing = make_listing(
        product=make_product(category=consumable, slug="real-gloves", is_demo=False),
        supplier=verified,
        is_demo=False,
        sku="REAL",
    )
    medicine_listing = make_listing(
        product=make_product(category=medicine, slug="sample-tablet", name="Sample tablet", is_demo=False),
        supplier=verified,
        is_demo=False,
        sku="MED",
    )
    assert purchase_block_reason(demo_listing) == "Sample records cannot be purchased."
    assert purchase_block_reason(real_listing) is None
    assert "regulatory policy" in purchase_block_reason(medicine_listing)


@pytest.mark.django_db
def test_draft_listings_are_not_public(api):
    owner = make_user()
    category = make_category()
    supplier = make_supplier(owner=owner)
    product = make_product(category=category)
    make_listing(product=product, supplier=supplier, status=ListingStatus.DRAFT)
    assert api.get("/api/v1/catalog/products/").json()["data"] == []


@pytest.mark.django_db
def test_product_search_and_pagination(api):
    owner = make_user()
    category = make_category()
    supplier = make_supplier(owner=owner)
    make_listing(product=make_product(category=category, slug="gloves", name="Nitrile gloves"), supplier=supplier, sku="A")
    make_listing(
        product=make_product(category=category, slug="thermometer", name="Thermometer"),
        supplier=supplier,
        sku="B",
    )
    found = api.get("/api/v1/catalog/products/?q=therm")
    assert [item["slug"] for item in found.json()["data"]] == ["thermometer"]
    suppliers = api.get("/api/v1/catalog/suppliers/?q=Accra")
    assert suppliers.status_code == 200
    assert suppliers.json()["data"][0]["region"] == "Greater Accra"
    page = api.get("/api/v1/catalog/products/?page_size=1&ordering=name")
    assert page.json()["meta"]["pages"] == 2
    assert page.json()["meta"]["count"] == 2


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_seed_is_idempotent_and_keeps_pharmaceuticals_closed():
    call_command("seed_demo")
    call_command("seed_demo")
    policy = CategoryPolicy.objects.get(category__slug="authorized-pharmaceuticals")
    assert policy.checkout_enabled is False
    assert policy.requires_authorization is True
    products = api_products()
    assert products
    assert all(item["can_purchase"] is False for item in products)
    assert all(item["is_demo"] is True for item in products)


def api_products():
    from rest_framework.test import APIClient

    client = APIClient()
    response = client.get("/api/v1/catalog/products/")
    assert response.status_code == 200
    return response.json()["data"]

import uuid

import pytest
from rest_framework.test import APIClient

from conftest import bearer, post_json
from modules.catalog.models import ListingStatus, SupplierVerification
from modules.commerce.models import CartLine
from tests.factories import PASSWORD, make_category, make_listing, make_product, make_supplier, make_user


def _listing(*, demo=True, checkout=True, requires=False, stock=20, moq=2, status=ListingStatus.ACTIVE):
    suffix = uuid.uuid4().hex[:8]
    owner = make_user(email=f"owner-{suffix}@example.com")
    category = make_category(
        slug=f"cat-{suffix}",
        checkout=checkout,
        requires=requires,
    )
    if demo:
        supplier = make_supplier(owner=owner, slug=f"supplier-{suffix}")
    else:
        supplier = make_supplier(
            owner=owner,
            slug=f"supplier-{suffix}",
            status=SupplierVerification.VERIFIED,
            is_demo=False,
        )
    product = make_product(
        category=category,
        slug=f"product-{suffix}",
        is_demo=demo,
    )
    return make_listing(
        product=product,
        supplier=supplier,
        sku="SKU",
        stock=stock,
        moq=moq,
        status=status,
        is_demo=demo,
        price="10.00",
    )


@pytest.mark.django_db
def test_guest_cart_add_update_and_isolation(api, csrf_token):
    listing = _listing()
    created = post_json(
        api,
        "/api/v1/cart/lines/",
        {"listing_id": str(listing.id), "quantity": 2},
        csrf_token,
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["item_count"] == 2
    assert body["checkout_open"] is False
    assert body["lines"][0]["purchase_block_reason"] == "Sample records cannot be purchased."
    assert body["subtotal"]["amount"] == "20.00"
    line_id = body["lines"][0]["id"]

    other = APIClient(enforce_csrf_checks=True, HTTP_ORIGIN="http://testserver")
    assert other.get("/api/v1/cart/").json()["data"]["item_count"] == 0

    updated = api.patch(
        f"/api/v1/cart/lines/{line_id}/",
        {"quantity": 4},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["item_count"] == 4

    too_many = api.patch(
        f"/api/v1/cart/lines/{line_id}/",
        {"quantity": 21},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert too_many.status_code == 400
    assert too_many.json()["error"]["code"] == "validation_error"

    removed = api.delete(f"/api/v1/cart/lines/{line_id}/", HTTP_X_CSRFTOKEN=csrf_token)
    assert removed.status_code == 200
    assert removed.json()["data"]["lines"] == []


@pytest.mark.django_db
def test_cart_rejects_hidden_listings_and_short_quantities(api, csrf_token):
    listing = _listing(moq=5, stock=10)
    short = post_json(api, "/api/v1/cart/lines/", {"listing_id": str(listing.id), "quantity": 1}, csrf_token)
    assert short.status_code == 400

    draft = _listing(status=ListingStatus.DRAFT, moq=1)
    hidden = post_json(api, "/api/v1/cart/lines/", {"listing_id": str(draft.id), "quantity": 1}, csrf_token)
    assert hidden.status_code == 404
    assert CartLine.objects.count() == 0


@pytest.mark.django_db
def test_customer_carts_stay_separate_and_checkout_stays_closed(api, csrf_token):
    customer = make_user(email="customer@example.com")
    other = make_user(email="other@example.com")
    listing = _listing(demo=False, checkout=True)
    bearer(api, customer)
    added = api.post("/api/v1/cart/lines/", {"listing_id": str(listing.id), "quantity": 2}, format="json")
    assert added.status_code == 201
    assert added.json()["data"]["lines"][0]["purchase_block_reason"] is None

    bearer(api, other)
    assert api.get("/api/v1/cart/").json()["data"]["lines"] == []

    bearer(api, customer)
    refused = api.post("/api/v1/cart/checkout/", {}, format="json")
    assert refused.status_code == 409
    assert refused.json()["error"]["code"] == "checkout_closed"
    assert refused.json()["error"]["details"]["lines"][0]["reason"] == "Payment is not open in this release."


@pytest.mark.django_db
def test_pharmaceutical_line_cannot_check_out(api):
    listing = _listing(demo=False, checkout=False, requires=True, moq=1)
    customer = make_user(email="buyer@example.com")
    bearer(api, customer)
    added = api.post("/api/v1/cart/lines/", {"listing_id": str(listing.id), "quantity": 1}, format="json")
    assert added.status_code == 201
    refused = api.post("/api/v1/cart/checkout/", {}, format="json")
    assert refused.status_code == 409
    reason = refused.json()["error"]["details"]["lines"][0]["reason"]
    assert "regulatory policy" in reason


@pytest.mark.django_db
def test_login_moves_a_guest_cart_onto_the_customer(api, csrf_token):
    customer = make_user(email="ada@example.com")
    listing = _listing()
    added = post_json(api, "/api/v1/cart/lines/", {"listing_id": str(listing.id), "quantity": 2}, csrf_token)
    assert added.status_code == 201
    signed_in = post_json(
        api,
        "/api/v1/auth/login/",
        {"email": customer.email, "password": PASSWORD},
        csrf_token,
    )
    assert signed_in.status_code == 200
    cart = api.get("/api/v1/cart/")
    assert cart.status_code == 200
    assert cart.json()["data"]["item_count"] == 2
    assert api.cookies["ms_cart"].value == ""

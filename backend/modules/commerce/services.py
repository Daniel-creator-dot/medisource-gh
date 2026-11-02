import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from modules.catalog.constants import DEMO_LABEL
from modules.catalog.models import Listing
from modules.catalog.services import purchase_block_reason, visible_listings
from modules.commerce.models import Cart, CartLine, CartStatus

CHECKOUT_MESSAGE = (
    "Checkout is closed in this release. Sample records cannot be purchased, "
    "and authorized pharmaceuticals stay closed. No payment is taken."
)
EMPTY_CART = {
    "id": None,
    "line_count": 0,
    "item_count": 0,
    "lines": [],
    "subtotal": {"amount": "0.00", "currency": "GHS"},
    "checkout_open": False,
    "checkout_message": CHECKOUT_MESSAGE,
}


def _authenticated_user(request):
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return user
    return None


def _cookie_cart_id(request):
    raw = request.COOKIES.get(settings.CART_COOKIE)
    if not raw:
        return None
    try:
        return uuid.UUID(str(raw))
    except ValueError:
        return None


def peek_cart(request) -> Cart | None:
    user = _authenticated_user(request)
    if user is not None:
        return Cart.objects.filter(user=user, status=CartStatus.OPEN).first()
    cart_id = _cookie_cart_id(request)
    if cart_id is None:
        return None
    return Cart.objects.filter(pk=cart_id, user__isnull=True, status=CartStatus.OPEN).first()


def open_cart(request) -> tuple[Cart, bool]:
    user = _authenticated_user(request)
    if user is not None:
        cart, _created = Cart.objects.get_or_create(user=user, status=CartStatus.OPEN)
        return cart, False
    existing = peek_cart(request)
    if existing is not None:
        return existing, False
    return Cart.objects.create(status=CartStatus.OPEN), True


def _public_listing(listing_id) -> Listing:
    listing = (
        visible_listings()
        .select_related("master_product", "master_product__category__policy", "supplier")
        .filter(pk=listing_id)
        .first()
    )
    if listing is None:
        raise NotFound("This listing is not available.")
    return listing


def _check_quantity(listing: Listing, quantity: int) -> None:
    if quantity < listing.minimum_order_quantity:
        raise ValidationError({"quantity": f"The minimum order is {listing.minimum_order_quantity}."})
    if quantity > listing.stock_quantity:
        raise ValidationError({"quantity": f"Only {listing.stock_quantity} are in stock."})


@transaction.atomic
def add_line(cart: Cart, listing_id, quantity: int) -> CartLine:
    listing = _public_listing(listing_id)
    _check_quantity(listing, quantity)
    line = CartLine.objects.select_for_update().filter(cart=cart, listing=listing).first()
    if line is None:
        return CartLine.objects.create(cart=cart, listing=listing, quantity=quantity)
    new_quantity = line.quantity + quantity
    _check_quantity(listing, new_quantity)
    line.quantity = new_quantity
    line.save(update_fields=["quantity", "updated_at"])
    return line


@transaction.atomic
def set_quantity(line: CartLine, quantity: int) -> CartLine:
    listing = _public_listing(line.listing_id)
    _check_quantity(listing, quantity)
    line.quantity = quantity
    line.save(update_fields=["quantity", "updated_at"])
    return line


def cart_line_or_404(request, line_id) -> CartLine:
    cart = peek_cart(request)
    if cart is None:
        raise NotFound("Cart line not found.")
    line = cart.lines.filter(pk=line_id).first()
    if line is None:
        raise NotFound("Cart line not found.")
    return line


def _money(amount: Decimal) -> str:
    return f"{amount.quantize(Decimal('0.01'))}"


def cart_payload(cart: Cart | None) -> dict:
    if cart is None:
        return dict(EMPTY_CART)
    lines = []
    total = Decimal("0.00")
    currency = "GHS"
    queryset = cart.lines.select_related(
        "listing__master_product__category__policy",
        "listing__supplier",
    ).order_by("created_at")
    for line in queryset:
        listing = line.listing
        product = listing.master_product
        currency = listing.currency
        line_total = (listing.price_amount * line.quantity).quantize(Decimal("0.01"))
        total += line_total
        lines.append(
            {
                "id": str(line.id),
                "quantity": line.quantity,
                "listing_id": str(listing.id),
                "sku": listing.sku,
                "price_amount": _money(listing.price_amount),
                "line_total": _money(line_total),
                "currency": listing.currency,
                "stock_quantity": listing.stock_quantity,
                "minimum_order_quantity": listing.minimum_order_quantity,
                "product_name": product.name,
                "product_slug": product.slug,
                "supplier_name": listing.supplier.display_name,
                "supplier_slug": listing.supplier.slug,
                "is_demo": listing.is_demo or listing.supplier.is_demo or product.is_demo,
                "demo_label": DEMO_LABEL if listing.is_demo or listing.supplier.is_demo or product.is_demo else None,
                "purchase_block_reason": purchase_block_reason(listing),
            }
        )
    return {
        "id": str(cart.id),
        "line_count": len(lines),
        "item_count": sum(line["quantity"] for line in lines),
        "lines": lines,
        "subtotal": {"amount": _money(total), "currency": currency},
        "checkout_open": False,
        "checkout_message": CHECKOUT_MESSAGE,
    }


def checkout_refusal(cart: Cart) -> list[dict]:
    payload = cart_payload(cart)
    return [
        {
            "line_id": line["id"],
            "product_name": line["product_name"],
            "reason": line["purchase_block_reason"] or "Payment is not open in this release.",
        }
        for line in payload["lines"]
    ]


@transaction.atomic
def claim_guest_cart(request, user, response) -> None:
    from modules.commerce.cookies import clear_cart_cookie

    cart_id = _cookie_cart_id(request)
    if cart_id is None:
        return
    guest = Cart.objects.filter(pk=cart_id, user__isnull=True, status=CartStatus.OPEN).first()
    clear_cart_cookie(response)
    if guest is None:
        return
    user_cart, _created = Cart.objects.get_or_create(user=user, status=CartStatus.OPEN)
    if guest.id == user_cart.id:
        return
    for line in guest.lines.select_related("listing"):
        listing = line.listing
        if not visible_listings().filter(pk=listing.id).exists():
            continue
        target = min(line.quantity, listing.stock_quantity)
        if target < listing.minimum_order_quantity:
            continue
        existing = CartLine.objects.select_for_update().filter(cart=user_cart, listing=listing).first()
        if existing is None:
            CartLine.objects.create(cart=user_cart, listing=listing, quantity=target)
            continue
        combined = min(existing.quantity + target, listing.stock_quantity)
        if combined >= listing.minimum_order_quantity:
            existing.quantity = combined
            existing.save(update_fields=["quantity", "updated_at"])
    guest.delete()

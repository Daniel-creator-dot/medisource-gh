from django.db.models import Count, Exists, Min, OuterRef, Prefetch, Q
from django.http import Http404

from modules.catalog.models import (
    Category,
    Listing,
    ListingStatus,
    MasterProduct,
    Supplier,
    SupplierVerification,
)
from modules.organizations.models import OrganizationStatus

PUBLIC_SUPPLIER_STATUSES = (SupplierVerification.DEMO, SupplierVerification.VERIFIED)


def purchase_block_reason(listing: Listing) -> str | None:
    supplier = listing.supplier
    policy = getattr(listing.master_product.category, "policy", None)
    if listing.is_demo or supplier.is_demo or supplier.verification_status == SupplierVerification.DEMO:
        return "Sample records cannot be purchased."
    if supplier.verification_status != SupplierVerification.VERIFIED:
        return "This supplier is not verified."
    if supplier.organization.status != OrganizationStatus.ACTIVE:
        return "This supplier organization is not active."
    if listing.status != ListingStatus.ACTIVE:
        return "This listing is not active."
    if policy is None or not policy.checkout_enabled:
        return "This category is not open for checkout under the current regulatory policy."
    if policy.requires_authorization:
        return "This category requires an authorization step that is not available yet."
    if listing.stock_quantity < listing.minimum_order_quantity:
        return "Available stock is below the minimum order quantity."
    return None


def visible_listings():
    return Listing.objects.filter(
        status=ListingStatus.ACTIVE,
        supplier__verification_status__in=PUBLIC_SUPPLIER_STATUSES,
        supplier__organization__status=OrganizationStatus.ACTIVE,
    )


def public_products():
    visible = visible_listings()
    return (
        MasterProduct.objects.annotate(
            has_public_listing=Exists(visible.filter(master_product_id=OuterRef("pk"))),
            lowest_price_amount=Min(
                "listings__price_amount",
                filter=Q(
                    listings__status=ListingStatus.ACTIVE,
                    listings__supplier__verification_status__in=PUBLIC_SUPPLIER_STATUSES,
                    listings__supplier__organization__status=OrganizationStatus.ACTIVE,
                ),
            ),
        )
        .filter(has_public_listing=True)
        .select_related("category", "category__policy")
        .prefetch_related(
            Prefetch(
                "listings",
                queryset=visible.select_related("supplier", "supplier__organization", "master_product__category__policy"),
                to_attr="public_listings",
            )
        )
    )


def filter_products(params):
    queryset = public_products()
    query = (params.get("q") or "").strip()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(generic_name__icontains=query)
            | Q(manufacturer__icontains=query)
            | Q(description__icontains=query)
        )
    category = (params.get("category") or "").strip()
    if category:
        queryset = queryset.filter(category__slug=category)
    supplier = (params.get("supplier") or "").strip()
    if supplier:
        queryset = queryset.filter(
            id__in=visible_listings().filter(supplier__slug=supplier).values("master_product_id")
        )
    ordering = params.get("ordering") or "name"
    if ordering == "price":
        return queryset.order_by("lowest_price_amount", "name")
    if ordering == "-price":
        return queryset.order_by("-lowest_price_amount", "name")
    return queryset.order_by("name")


def get_public_product(slug: str) -> MasterProduct:
    product = public_products().filter(slug=slug).first()
    if product is None:
        raise Http404()
    return product


def public_categories():
    return (
        Category.objects.select_related("policy")
        .annotate(
            product_count=Count(
                "products",
                filter=Q(
                    products__listings__status=ListingStatus.ACTIVE,
                    products__listings__supplier__verification_status__in=PUBLIC_SUPPLIER_STATUSES,
                    products__listings__supplier__organization__status=OrganizationStatus.ACTIVE,
                ),
                distinct=True,
            )
        )
        .order_by("sort_order", "name")
    )


def public_suppliers():
    return (
        Supplier.objects.filter(
            verification_status__in=PUBLIC_SUPPLIER_STATUSES,
            organization__status=OrganizationStatus.ACTIVE,
        )
        .annotate(
            active_listing_count=Count(
                "listings",
                filter=Q(listings__status=ListingStatus.ACTIVE),
                distinct=True,
            )
        )
        .order_by("display_name")
    )


def get_public_supplier(slug: str) -> Supplier:
    supplier = (
        public_suppliers()
        .prefetch_related(
            Prefetch(
                "listings",
                queryset=Listing.objects.filter(status=ListingStatus.ACTIVE).select_related(
                    "master_product",
                    "master_product__category",
                    "master_product__category__policy",
                    "supplier",
                    "supplier__organization",
                ),
                to_attr="public_listings",
            )
        )
        .filter(slug=slug)
        .first()
    )
    if supplier is None:
        raise Http404()
    return supplier

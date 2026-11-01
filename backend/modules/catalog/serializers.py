from rest_framework import serializers

from modules.catalog.constants import DEMO_LABEL
from modules.catalog.models import Category, Listing, MasterProduct, Supplier
from modules.catalog.services import purchase_block_reason


class SupplierCardSerializer(serializers.ModelSerializer):
    demo_label = serializers.SerializerMethodField()
    active_listing_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            "id",
            "display_name",
            "slug",
            "summary",
            "city",
            "region",
            "verification_status",
            "is_demo",
            "demo_label",
            "active_listing_count",
        ]

    def get_demo_label(self, obj: Supplier) -> str | None:
        return DEMO_LABEL if obj.is_demo else None

    def get_active_listing_count(self, obj: Supplier) -> int | None:
        return getattr(obj, "active_listing_count", None)


class ListingSerializer(serializers.ModelSerializer):
    supplier = SupplierCardSerializer()
    can_purchase = serializers.SerializerMethodField()
    purchase_block_reason = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "sku",
            "price_amount",
            "currency",
            "stock_quantity",
            "minimum_order_quantity",
            "lead_time_days",
            "warehouse_name",
            "delivery_zones",
            "status",
            "is_demo",
            "supplier",
            "can_purchase",
            "purchase_block_reason",
        ]

    def get_can_purchase(self, obj: Listing) -> bool:
        return purchase_block_reason(obj) is None

    def get_purchase_block_reason(self, obj: Listing) -> str | None:
        return purchase_block_reason(obj)


class ProductCardSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    category_slug = serializers.CharField(source="category.slug")
    lowest_price = serializers.SerializerMethodField()
    supplier_count = serializers.SerializerMethodField()
    can_purchase = serializers.SerializerMethodField()
    purchase_block_reason = serializers.SerializerMethodField()
    demo_label = serializers.SerializerMethodField()

    class Meta:
        model = MasterProduct
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "manufacturer",
            "pack_size",
            "unit_of_measure",
            "is_demo",
            "demo_label",
            "category_name",
            "category_slug",
            "lowest_price",
            "supplier_count",
            "can_purchase",
            "purchase_block_reason",
        ]

    def get_lowest_price(self, obj: MasterProduct):
        listings = getattr(obj, "public_listings", [])
        if not listings:
            return None
        best = min(listings, key=lambda item: item.price_amount)
        return {"amount": str(best.price_amount), "currency": best.currency}

    def get_supplier_count(self, obj: MasterProduct) -> int:
        return len({item.supplier_id for item in getattr(obj, "public_listings", [])})

    def get_can_purchase(self, obj: MasterProduct) -> bool:
        return self.get_purchase_block_reason(obj) is None

    def get_purchase_block_reason(self, obj: MasterProduct) -> str | None:
        listings = getattr(obj, "public_listings", [])
        if not listings:
            return "This product has no public listing."
        reasons = [purchase_block_reason(item) for item in listings]
        if any(reason is None for reason in reasons):
            return None
        return reasons[0]

    def get_demo_label(self, obj: MasterProduct) -> str | None:
        return DEMO_LABEL if obj.is_demo else None


class ProductDetailSerializer(ProductCardSerializer):
    listings = serializers.SerializerMethodField()

    class Meta(ProductCardSerializer.Meta):
        fields = ProductCardSerializer.Meta.fields + [
            "generic_name",
            "description",
            "specification",
            "strength",
            "dosage_form",
            "gtin",
            "regulatory_notes",
            "listings",
        ]

    def get_listings(self, obj: MasterProduct):
        return ListingSerializer(getattr(obj, "public_listings", []), many=True).data


class CategorySerializer(serializers.ModelSerializer):
    checkout_enabled = serializers.SerializerMethodField()
    requires_authorization = serializers.SerializerMethodField()
    policy_reference = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "checkout_enabled",
            "requires_authorization",
            "policy_reference",
            "product_count",
        ]

    def get_checkout_enabled(self, obj: Category) -> bool:
        policy = getattr(obj, "policy", None)
        return bool(policy and policy.checkout_enabled)

    def get_requires_authorization(self, obj: Category) -> bool:
        policy = getattr(obj, "policy", None)
        return bool(policy and policy.requires_authorization)

    def get_policy_reference(self, obj: Category) -> str:
        policy = getattr(obj, "policy", None)
        return policy.policy_reference if policy else ""


class SupplierListingSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="master_product.name")
    product_slug = serializers.CharField(source="master_product.slug")
    can_purchase = serializers.SerializerMethodField()
    purchase_block_reason = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id",
            "sku",
            "price_amount",
            "currency",
            "stock_quantity",
            "minimum_order_quantity",
            "lead_time_days",
            "warehouse_name",
            "delivery_zones",
            "is_demo",
            "product_name",
            "product_slug",
            "can_purchase",
            "purchase_block_reason",
        ]

    def get_can_purchase(self, obj: Listing) -> bool:
        return purchase_block_reason(obj) is None

    def get_purchase_block_reason(self, obj: Listing) -> str | None:
        return purchase_block_reason(obj)


class SupplierDetailSerializer(SupplierCardSerializer):
    listings = serializers.SerializerMethodField()

    class Meta(SupplierCardSerializer.Meta):
        fields = SupplierCardSerializer.Meta.fields + ["listings"]

    def get_listings(self, obj: Supplier):
        return SupplierListingSerializer(getattr(obj, "public_listings", []), many=True).data

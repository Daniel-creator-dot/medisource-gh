from django.contrib import admin

from modules.catalog.models import Category, CategoryPolicy, Listing, MasterProduct, Supplier


class CategoryPolicyInline(admin.StackedInline):
    model = CategoryPolicy
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryPolicyInline]


@admin.register(MasterProduct)
class MasterProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "manufacturer", "is_demo")
    list_filter = ("category", "is_demo")
    search_fields = ("name", "brand", "manufacturer")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("display_name", "verification_status", "region", "is_demo")
    list_filter = ("verification_status", "is_demo")
    search_fields = ("display_name", "slug")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("sku", "master_product", "supplier", "price_amount", "stock_quantity", "status", "is_demo")
    list_filter = ("status", "is_demo")
    search_fields = ("sku", "master_product__name", "supplier__display_name")

from django.contrib import admin

from modules.commerce.models import Cart, CartLine


class CartLineInline(admin.TabularInline):
    model = CartLine
    extra = 0
    raw_id_fields = ("listing",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "updated_at")
    raw_id_fields = ("user",)
    inlines = [CartLineInline]

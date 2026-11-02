from django.conf import settings
from django.db import models

from common.models import UUIDTimeStampedModel


class CartStatus(models.TextChoices):
    OPEN = "open", "Open"


class Cart(UUIDTimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    status = models.CharField(max_length=16, choices=CartStatus.choices, default=CartStatus.OPEN)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=CartStatus.OPEN),
                name="one_open_cart_per_user",
            )
        ]

    def __str__(self) -> str:
        owner = self.user_id or "guest"
        return f"Cart {self.id} ({owner})"


class CartLine(UUIDTimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="lines")
    listing = models.ForeignKey("catalog.Listing", on_delete=models.PROTECT, related_name="cart_lines")
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "listing"], name="unique_cart_listing"),
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="cart_line_quantity_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.listing_id}"

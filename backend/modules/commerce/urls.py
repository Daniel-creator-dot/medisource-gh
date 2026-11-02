from django.urls import path

from modules.commerce.views import CartCheckoutView, CartLineCreateView, CartLineDetailView, CartView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("lines/", CartLineCreateView.as_view(), name="cart-lines"),
    path("lines/<uuid:line_id>/", CartLineDetailView.as_view(), name="cart-line"),
    path("checkout/", CartCheckoutView.as_view(), name="cart-checkout"),
]

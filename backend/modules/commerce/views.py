from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.commerce.cookies import set_cart_cookie
from modules.commerce.serializers import CartLineWriteSerializer, CartQuantitySerializer
from modules.commerce.services import (
    CHECKOUT_MESSAGE,
    add_line,
    cart_line_or_404,
    cart_payload,
    checkout_refusal,
    open_cart,
    peek_cart,
    set_quantity,
)


class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return ok(cart_payload(peek_cart(request)))


class CartLineCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CartLineWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, should_set_cookie = open_cart(request)
        add_line(cart, serializer.validated_data["listing_id"], serializer.validated_data["quantity"])
        response = ok(cart_payload(cart), status=201)
        if should_set_cookie:
            set_cart_cookie(response, cart.id)
        return response


class CartLineDetailView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, line_id):
        serializer = CartQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        line = cart_line_or_404(request, line_id)
        set_quantity(line, serializer.validated_data["quantity"])
        return ok(cart_payload(peek_cart(request)))

    def delete(self, request, line_id):
        line = cart_line_or_404(request, line_id)
        cart = line.cart
        line.delete()
        return ok(cart_payload(cart))


class CartCheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cart = peek_cart(request)
        if cart is None or not cart.lines.exists():
            return error_response("cart_empty", "Your cart is empty.", 400)
        return error_response(
            "checkout_closed",
            CHECKOUT_MESSAGE,
            409,
            details={"lines": checkout_refusal(cart)},
        )

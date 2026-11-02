from django.conf import settings


def _cookie_samesite() -> str:
    return "None" if not settings.DEBUG else "Lax"


def set_cart_cookie(response, cart_id) -> None:
    response.set_cookie(
        settings.CART_COOKIE,
        str(cart_id),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        secure=not settings.DEBUG,
        samesite=_cookie_samesite(),
        path="/",
    )


def clear_cart_cookie(response) -> None:
    response.delete_cookie(settings.CART_COOKIE, path="/", samesite=_cookie_samesite())

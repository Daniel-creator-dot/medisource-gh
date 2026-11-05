from django.conf import settings


def cookie_samesite() -> str:
    return "None" if not settings.DEBUG else "Lax"


def set_auth_cookies(response, access: str, refresh: str) -> None:
    secure = not settings.DEBUG
    samesite = cookie_samesite()
    response.set_cookie(
        settings.AUTH_ACCESS_COOKIE,
        access,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE,
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/api/v1/auth/",
    )


def clear_auth_cookies(response) -> None:
    samesite = cookie_samesite()
    response.delete_cookie(settings.AUTH_ACCESS_COOKIE, path="/", samesite=samesite)
    response.delete_cookie(settings.AUTH_REFRESH_COOKIE, path="/api/v1/auth/", samesite=samesite)

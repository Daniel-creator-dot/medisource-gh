from django.conf import settings


def client_wants_bearer(request) -> bool:
    return request.headers.get("X-Client") == "mobile"


def _cookie_samesite() -> str:
    # The website and API are different hosts on Render, so the browser
    # only attaches the session cookie to credentialed API calls when
    # SameSite is None. Local HTTP keeps Lax.
    return "None" if not settings.DEBUG else "Lax"


def set_auth_cookies(response, access: str, refresh: str) -> None:
    secure = not settings.DEBUG
    samesite = _cookie_samesite()
    access_age = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
    refresh_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        settings.AUTH_ACCESS_COOKIE,
        access,
        max_age=access_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE,
        refresh,
        max_age=refresh_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/api/v1/auth/",
    )


def clear_auth_cookies(response) -> None:
    samesite = _cookie_samesite()
    response.delete_cookie(settings.AUTH_ACCESS_COOKIE, path="/", samesite=samesite)
    response.delete_cookie(settings.AUTH_REFRESH_COOKIE, path="/api/v1/auth/", samesite=samesite)

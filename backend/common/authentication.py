from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieOrBearerJWTAuthentication(JWTAuthentication):
    """Accept a bearer header for mobile clients, or the HttpOnly access cookie for browsers."""

    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw = self.get_raw_token(header)
            if raw is None:
                return None
            validated = self.get_validated_token(raw)
            return self.get_user(validated), validated

        raw_cookie = request.COOKIES.get(settings.AUTH_ACCESS_COOKIE)
        if not raw_cookie:
            return None
        validated = self.get_validated_token(raw_cookie)
        return self.get_user(validated), validated

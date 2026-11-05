from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieOrBearerJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)
        raw = request.COOKIES.get(settings.AUTH_ACCESS_COOKIE)
        if not raw:
            return None
        validated = self.get_validated_token(raw)
        return self.get_user(validated), validated

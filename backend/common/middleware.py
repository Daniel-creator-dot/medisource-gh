from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin


class _CsrfReason(CsrfViewMiddleware):
    """Return the rejection reason instead of an HTML response.

    DRF marks API views as CSRF-exempt, so the stock middleware never sees them.
    Browser cookie sessions still need a real CSRF check.
    """

    def _reject(self, request, reason):
        return reason


class CookieAuthCsrfMiddleware(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            return None
        if not request.path.startswith("/api/"):
            return None
        if request.headers.get("Authorization", "").startswith("Bearer "):
            return None
        if request.headers.get("X-Client") == "mobile":
            return None

        check = _CsrfReason(lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, lambda request: None, (), {})
        if reason:
            return JsonResponse(
                {
                    "error": {
                        "code": "csrf_failed",
                        "message": "CSRF verification failed.",
                        "details": None,
                    }
                },
                status=403,
            )
        return None

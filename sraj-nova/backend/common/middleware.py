from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin


class _CsrfReason(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


class ApiSafeCsrfMiddleware(CsrfViewMiddleware):
    """API failures stay JSON. The HTML CSRF page cannot be parsed by the browser."""

    def _reject(self, request, reason):
        if request.path.startswith("/api/"):
            return JsonResponse(
                {"error": {"code": "csrf_failed", "message": "CSRF verification failed.", "details": None}},
                status=403,
            )
        return super()._reject(request, reason)


class EnsureApiSlashMiddleware(MiddlewareMixin):
    """Keep slash-sensitive API routes reachable through the web proxy."""

    def process_request(self, request):
        if request.path.startswith("/api/") and not request.path.endswith("/"):
            request.path_info = f"{request.path_info}/"
        return None


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
                {"error": {"code": "csrf_failed", "message": "CSRF verification failed.", "details": None}},
                status=403,
            )
        return None

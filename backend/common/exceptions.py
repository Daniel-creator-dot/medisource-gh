from django.http import Http404
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.views import exception_handler


def _detail_message(data) -> str | None:
    if isinstance(data, dict) and "detail" in data:
        detail = data["detail"]
        if isinstance(detail, list):
            return " ".join(str(item) for item in detail)
        return str(detail)
    return None


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    code = "error"
    details = response.data
    message = "Request could not be completed."

    if isinstance(exc, ValidationError):
        code = "validation_error"
        message = "Some fields need attention."
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        code = "unauthenticated"
        message = _detail_message(response.data) or "Authentication is required."
        details = None
    elif isinstance(exc, PermissionDenied):
        code = "forbidden"
        message = _detail_message(response.data) or "You do not have access to this resource."
        details = None
    elif isinstance(exc, (NotFound, Http404)):
        code = "not_found"
        message = _detail_message(response.data) or "Resource not found."
        details = None
    elif isinstance(exc, Throttled):
        code = "rate_limited"
        message = "Too many requests. Please wait and try again."
        details = None
    elif isinstance(exc, MethodNotAllowed):
        code = "method_not_allowed"
        message = "This action is not available."
        details = None
    else:
        extracted = _detail_message(response.data)
        if extracted:
            message = extracted
            if isinstance(response.data, dict) and set(response.data.keys()) == {"detail"}:
                details = None

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response

import logging

from django.http import Http404, JsonResponse
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_not_found(request, exception):
    if request.path.startswith("/api/"):
        return JsonResponse(
            {"error": {"code": "not_found", "message": "Resource not found.", "details": None}},
            status=404,
        )
    from django.views.defaults import page_not_found

    return page_not_found(request, exception)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        if isinstance(exc, Http404):
            return None
        logger.exception("Unhandled API error")
        return Response(
            {"error": {"code": "server_error", "message": "The request could not be completed.", "details": None}},
            status=500,
        )
    code = "error"
    message = "Request could not be completed."
    details = response.data
    if isinstance(exc, ValidationError):
        code = "validation_error"
        message = "Some fields need attention."
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        code = "unauthenticated"
        message = "Authentication is required."
        details = None
    elif isinstance(exc, PermissionDenied):
        code = "forbidden"
        message = "You do not have access to this resource."
        details = None
    elif isinstance(exc, NotFound):
        code = "not_found"
        message = "Resource not found."
        details = None
    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response

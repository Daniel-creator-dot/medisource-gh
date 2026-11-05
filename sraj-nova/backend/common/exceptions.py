from django.http import Http404
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        if isinstance(exc, Http404):
            return None
        return None
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

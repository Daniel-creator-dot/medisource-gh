from rest_framework.response import Response


def ok(data, *, status=200, meta=None):
    return Response({"data": data, "meta": meta or {}}, status=status)


def error_response(code: str, message: str, status: int, details=None):
    return Response({"error": {"code": code, "message": message, "details": details}}, status=status)

from django.middleware.csrf import get_token
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from common.api import error_response, ok
from modules.governance.services import record_audit
from modules.identity.cookies import clear_auth_cookies, set_auth_cookies
from modules.identity.serializers import CodeSerializer, LoginSerializer, UserSerializer
from modules.identity.models import AgencyRole, User
from modules.identity.services import (
    authenticate_user,
    begin_enrollment,
    confirm_enrollment,
    issue_token_pair,
    owner_must_enroll,
    verify_totp,
)


def _session(user, status=200):
    access, refresh = issue_token_pair(user)
    response = ok({"user": UserSerializer(user).data}, status=status)
    set_auth_cookies(response, access, refresh)
    return response


class CsrfView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return ok({"csrf_token": get_token(request)})


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_user(email=serializer.validated_data["email"], password=serializer.validated_data["password"])
        if user is None or not user.is_active:
            return error_response("invalid_credentials", "Email or password is incorrect.", 401)
        if owner_must_enroll(user):
            return error_response(
                "mfa_enrollment_required",
                "The agency owner must enroll an authenticator before a session is issued.",
                403,
            )
        if user.mfa_enabled:
            return ok({"mfa_required": True, "user": None})
        record_audit(actor=user, action="auth.login", resource_type="user", resource_id=user.id)
        return _session(user)


class MfaVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        login = LoginSerializer(data=request.data)
        login.is_valid(raise_exception=True)
        code = CodeSerializer(data=request.data)
        code.is_valid(raise_exception=True)
        user = authenticate_user(email=login.validated_data["email"], password=login.validated_data["password"])
        if user is None or not verify_totp(user, code.validated_data["code"]):
            return error_response("invalid_credentials", "Email, password, or authenticator code is incorrect.", 401)
        record_audit(actor=user, action="auth.mfa_verified", resource_type="user", resource_id=user.id)
        return _session(user)


class MfaEnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uri = begin_enrollment(request.user)
        return ok({"provisioning_uri": uri})


class MfaConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not confirm_enrollment(request.user, serializer.validated_data["code"]):
            return error_response("invalid_code", "The authenticator code was not accepted.", 400)
        return ok({"mfa_enabled": True})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok(UserSerializer(request.user).data)


class AccessUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != AgencyRole.AGENCY_OWNER:
            raise PermissionDenied()
        users = User.objects.order_by("email")
        return ok(
            [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.get_full_name(),
                    "role": user.role,
                    "mfa_enabled": user.mfa_enabled,
                    "is_demo": user.is_demo,
                }
                for user in users
            ]
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = ok({"logged_out": True})
        clear_auth_cookies(response)
        return response

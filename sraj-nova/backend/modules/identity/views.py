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
    ROLE_LABELS,
    RoleAssignmentError,
    account_settings,
    assign_role,
    assignable_roles,
    authenticate_user,
    begin_enrollment,
    change_password,
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


class AccountSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok(account_settings(request.user))


class PasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current = request.data.get("current_password") or ""
        new = request.data.get("new_password") or ""
        try:
            change_password(request.user, current, new)
        except RoleAssignmentError as exc:
            return error_response("invalid_password", exc.message, 400)
        record_audit(actor=request.user, action="auth.password_changed", resource_type="user", resource_id=request.user.id)
        return ok({"changed": True})


def _account_row(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.get_full_name(),
        "role": user.role,
        "role_label": ROLE_LABELS[user.role],
        "client_name": user.client.legal_name if user.client_id else None,
        "employee_number": user.employee.agency_employee_number if user.employee_id else None,
        "assignable_roles": [{"value": role, "label": ROLE_LABELS[role]} for role in assignable_roles(user)],
        "mfa_enabled": user.mfa_enabled,
        "is_demo": user.is_demo,
    }


class AccessUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != AgencyRole.AGENCY_OWNER:
            raise PermissionDenied()
        users = User.objects.select_related("client", "employee").order_by("email")
        return ok([_account_row(user) for user in users])


class AssignRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.role != AgencyRole.AGENCY_OWNER:
            raise PermissionDenied()
        target = User.objects.select_related("client", "employee").filter(pk=user_id).first()
        if target is None:
            from rest_framework.exceptions import NotFound

            raise NotFound()
        try:
            assign_role(target, request.data.get("role") or "")
        except RoleAssignmentError as exc:
            return error_response("invalid_role", exc.message, 400)
        record_audit(actor=request.user, action="auth.role_changed", resource_type="user", resource_id=target.id)
        target.refresh_from_db()
        return ok(_account_row(target))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = ok({"logged_out": True})
        clear_auth_cookies(response)
        return response

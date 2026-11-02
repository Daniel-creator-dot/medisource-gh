from django.conf import settings
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from common.api import error_response, ok
from common.pagination import EnvelopePagination
from modules.audit.services import record_audit
from modules.identity.cookies import clear_auth_cookies, client_wants_bearer, set_auth_cookies
from modules.identity.models import Address
from modules.identity.serializers import (
    AddressSerializer,
    LoginSerializer,
    MfaCodeSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    TokenCodeSerializer,
    UserSerializer,
)
from modules.identity.services import (
    MFA_ENROLL_SALT,
    MFA_LOGIN_SALT,
    authenticate_user,
    begin_totp,
    blacklist_refresh,
    confirm_email,
    confirm_password_reset,
    confirm_totp,
    create_address,
    decide_login,
    delete_address,
    issue_token_pair,
    register_customer,
    request_email_verification,
    request_password_reset,
    update_address,
    user_from_signed_token,
    verify_totp,
)
from modules.identity.throttles import AuthRateThrottle, AuthUserRateThrottle
from modules.notifications.services import notify_welcome
from modules.organizations.models import Membership
from modules.organizations.serializers import MembershipSerializer


def _session_payload(user, *, access=None, refresh=None, mfa_required=False, mfa_token=None):
    return {
        "user": None if mfa_required else UserSerializer(user).data,
        "mfa_required": mfa_required,
        "enrollment_required": False,
        "access": access,
        "refresh": refresh,
        "mfa_token": mfa_token,
    }


def _issue_session(request, user, status=200):
    access, refresh = issue_token_pair(user)
    if client_wants_bearer(request):
        return ok(_session_payload(user, access=access, refresh=refresh), status=status)
    response = ok(_session_payload(user), status=status)
    set_auth_cookies(response, access, refresh)
    from modules.commerce.services import claim_guest_cart

    claim_guest_cart(request, user, response)
    return response


class CsrfView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return ok({"csrf_token": get_token(request)})


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_customer(**serializer.validated_data, request=request)
        notify_welcome(user)
        record_audit(actor=user, action="auth.session_started", resource_type="user", resource_id=user.id, request=request)
        return _issue_session(request, user, status=201)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = authenticate_user(email=email, password=serializer.validated_data["password"], request=request)
        if user is None:
            record_audit(
                action="auth.login_failed",
                resource_type="user",
                metadata={"email": email.strip().lower()},
                request=request,
            )
            return error_response("invalid_credentials", "Email or password is incorrect.", 401)
        decision = decide_login(user)
        if decision.kind == "enrollment":
            record_audit(actor=user, action="auth.mfa_enrollment_required", resource_type="user", resource_id=user.id, request=request)
            return error_response(
                "mfa_enrollment_required",
                "This account must enroll an authenticator before it can sign in.",
                403,
                details={"enrollment_token": decision.enrollment_token},
            )
        if decision.kind == "mfa":
            return ok(_session_payload(user, mfa_required=True, mfa_token=decision.mfa_token))
        record_audit(actor=user, action="auth.login_succeeded", resource_type="user", resource_id=user.id, request=request)
        return _issue_session(request, user)


class MfaVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = MfaCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_from_signed_token(serializer.validated_data.get("mfa_token", ""), MFA_LOGIN_SALT, 300)
        if user is None or not verify_totp(user, serializer.validated_data["code"]):
            return error_response("invalid_token", "The authenticator code or sign-in step is no longer valid.", 401)
        record_audit(actor=user, action="auth.mfa_verified", resource_type="user", resource_id=user.id, request=request)
        return _issue_session(request, user)


class MfaEnrollView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthUserRateThrottle, AuthRateThrottle]

    def post(self, request):
        user = _user_for_enrollment(request)
        if user is None:
            return error_response("unauthenticated", "Authentication is required.", 401)
        return ok(begin_totp(user))


class MfaConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthUserRateThrottle, AuthRateThrottle]

    def post(self, request):
        serializer = MfaCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _user_for_enrollment(request, serializer.validated_data.get("enrollment_token", ""))
        if user is None:
            return error_response("unauthenticated", "Authentication is required.", 401)
        confirm_totp(user, serializer.validated_data["code"])
        user.refresh_from_db()
        return ok({"mfa_enabled": user.mfa_enabled})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE) or request.data.get("refresh", "")
        if request.user.is_authenticated:
            record_audit(actor=request.user, action="auth.logout", resource_type="user", resource_id=request.user.id, request=request)
        blacklist_refresh(raw)
        response = ok({"logged_out": True})
        clear_auth_cookies(response)
        return response


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        raw = request.data.get("refresh") or request.COOKIES.get(settings.AUTH_REFRESH_COOKIE)
        if not raw:
            return error_response("invalid_token", "The refresh token is missing.", 401)
        try:
            old = RefreshToken(raw)
            user_id = old["user_id"]
            old.blacklist()
        except TokenError:
            return error_response("invalid_token", "The refresh token is no longer valid.", 401)
        from modules.identity.models import User

        user = User.objects.filter(pk=user_id, is_active=True).first()
        if user is None:
            return error_response("invalid_token", "The refresh token is no longer valid.", 401)
        return _issue_session(request, user)


class MeView(APIView):
    def get(self, request):
        return ok(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ok(serializer.data)


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = TokenCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not confirm_email(serializer.validated_data["token"]):
            return error_response("invalid_token", "This verification link is invalid or has expired.", 400)
        return ok({"email_verified": True})


class ResendVerificationView(APIView):
    throttle_classes = [AuthUserRateThrottle]

    def post(self, request):
        request_email_verification(request.user)
        return ok({"sent": True})


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        if email:
            request_password_reset(email)
        return ok({"message": "If an account exists for that email, password reset instructions have been sent."})


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not confirm_password_reset(
            raw_token=serializer.validated_data["token"],
            password=serializer.validated_data["password"],
        ):
            return error_response("invalid_token", "This reset link is invalid or has expired.", 400)
        return ok({"reset": True})


class AddressListCreateView(APIView):
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        paginator = EnvelopePagination()
        page = paginator.paginate_queryset(addresses, request)
        return paginator.get_paginated_response(AddressSerializer(page, many=True).data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = create_address(request.user, **serializer.validated_data)
        return ok(AddressSerializer(address).data, status=201)


class AddressDetailView(APIView):
    def get(self, request, address_id):
        return ok(AddressSerializer(_own_address(request, address_id)).data)

    def patch(self, request, address_id):
        address = _own_address(request, address_id)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = update_address(address, **serializer.validated_data)
        return ok(AddressSerializer(updated).data)

    def delete(self, request, address_id):
        delete_address(_own_address(request, address_id))
        return ok({"deleted": True})


class MembershipListView(APIView):
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user, is_active=True).select_related("organization")
        return ok(MembershipSerializer(memberships, many=True).data)


def _own_address(request, address_id):
    return get_object_or_404(Address, pk=address_id, user=request.user)


def _user_for_enrollment(request, enrollment_token: str = ""):
    if request.user.is_authenticated:
        return request.user
    token = enrollment_token or request.data.get("enrollment_token", "")
    return user_from_signed_token(token, MFA_ENROLL_SALT, 600)

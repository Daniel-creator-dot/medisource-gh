from dataclasses import dataclass
from datetime import timedelta

import pyotp
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from modules.audit.services import record_audit
from modules.identity.crypto import (
    decrypt_secret,
    encrypt_secret,
    hash_token,
    new_raw_token,
    sign_user,
    unsign_user,
)
from modules.identity.models import Address, MfaFactor, OneTimeToken, PlatformRole, User

MFA_LOGIN_SALT = "medisource.mfa-login"
MFA_ENROLL_SALT = "medisource.mfa-enroll"


@dataclass
class LoginDecision:
    kind: str
    mfa_token: str = ""
    enrollment_token: str = ""


def issue_token_pair(user: User) -> tuple[str, str]:
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def blacklist_refresh(raw: str) -> None:
    if not raw:
        return
    try:
        token = RefreshToken(raw)
        token.blacklist()
    except TokenError:
        return


def blacklist_all_refresh_tokens(user: User) -> None:
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def needs_mfa_enrollment(user: User) -> bool:
    return bool(
        settings.MFA_REQUIRED_FOR_PRIVILEGED
        and user.platform_role in {PlatformRole.PLATFORM_ADMIN, PlatformRole.FINANCE_OFFICER}
        and not user.mfa_enabled
    )


def decide_login(user: User) -> LoginDecision:
    if needs_mfa_enrollment(user):
        return LoginDecision(
            "enrollment",
            enrollment_token=sign_user(user.id, MFA_ENROLL_SALT),
        )
    if user.mfa_enabled:
        return LoginDecision("mfa", mfa_token=sign_user(user.id, MFA_LOGIN_SALT))
    return LoginDecision("session")


def authenticate_user(*, email: str, password: str, request):
    return authenticate(request, email=email.strip().lower(), password=password)


def user_from_signed_token(token: str, salt: str, max_age: int) -> User | None:
    user_id = unsign_user(token or "", salt, max_age)
    if not user_id:
        return None
    return User.objects.filter(pk=user_id, is_active=True).first()


def register_customer(*, email: str, password: str, first_name: str, last_name: str, phone_number: str = "", request=None) -> User:
    validate_password(password)
    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone_number=phone_number.strip(),
            platform_role=PlatformRole.CUSTOMER,
        )
        raw = _issue_one_time_token(user, OneTimeToken.Purpose.EMAIL_VERIFY, hours=24)
        record_audit(
            actor=user,
            action="auth.registered",
            resource_type="user",
            resource_id=user.id,
            request=request,
        )
    _send_verification_email(user, raw)
    return user


def request_email_verification(user: User) -> None:
    if user.email_verified:
        return
    raw = _issue_one_time_token(user, OneTimeToken.Purpose.EMAIL_VERIFY, hours=24)
    _send_verification_email(user, raw)


def confirm_email(raw_token: str) -> bool:
    token = _consume_token(raw_token, OneTimeToken.Purpose.EMAIL_VERIFY)
    if token is None:
        return False
    user = token.user
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    record_audit(actor=user, action="auth.email_verified", resource_type="user", resource_id=user.id)
    return True


def request_password_reset(email: str) -> None:
    user = User.objects.filter(email=email.strip().lower(), is_active=True).first()
    if user is None:
        return
    raw = _issue_one_time_token(user, OneTimeToken.Purpose.PASSWORD_RESET, hours=1)
    link = f"{settings.WEB_ORIGIN}/forgot-password?token={raw}"
    send_mail(
        "Reset your MediSource GH password",
        (
            "Use this link within one hour to choose a new password.\n\n"
            f"{link}\n\n"
            "If you did not ask for a reset, you can ignore this message."
        ),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def confirm_password_reset(*, raw_token: str, password: str) -> bool:
    validate_password(password)
    token = _consume_token(raw_token, OneTimeToken.Purpose.PASSWORD_RESET)
    if token is None:
        return False
    user = token.user
    user.set_password(password)
    user.save(update_fields=["password"])
    blacklist_all_refresh_tokens(user)
    record_audit(actor=user, action="auth.password_reset", resource_type="user", resource_id=user.id)
    return True


def begin_totp(user: User) -> dict:
    if user.mfa_enabled:
        raise ValidationError("An authenticator is already enabled on this account.")
    secret = pyotp.random_base32()
    MfaFactor.objects.filter(
        user=user,
        method=MfaFactor.Method.TOTP,
        confirmed_at__isnull=True,
    ).delete()
    MfaFactor.objects.create(
        user=user,
        method=MfaFactor.Method.TOTP,
        secret_encrypted=encrypt_secret(secret),
        is_active=False,
    )
    uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="MediSource GH")
    return {"secret": secret, "provisioning_uri": uri}


def confirm_totp(user: User, code: str) -> None:
    factor = (
        MfaFactor.objects.filter(user=user, method=MfaFactor.Method.TOTP, confirmed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if factor is None:
        raise ValidationError("Start authenticator enrollment before confirming a code.")
    if not _code_matches(factor, code):
        raise ValidationError("That authenticator code is not valid.")
    with transaction.atomic():
        MfaFactor.objects.filter(user=user, method=MfaFactor.Method.TOTP, is_active=True).update(is_active=False)
        factor.confirmed_at = timezone.now()
        factor.is_active = True
        factor.save(update_fields=["confirmed_at", "is_active", "updated_at"])
        user.mfa_enabled = True
        user.save(update_fields=["mfa_enabled"])
    record_audit(actor=user, action="auth.mfa_enabled", resource_type="user", resource_id=user.id)


def verify_totp(user: User, code: str) -> bool:
    factor = MfaFactor.objects.filter(user=user, method=MfaFactor.Method.TOTP, is_active=True).first()
    if factor is None:
        return False
    return _code_matches(factor, code)


def create_address(user: User, **data) -> Address:
    make_default = data.pop("is_default", False) or not Address.objects.filter(user=user).exists()
    with transaction.atomic():
        try:
            with transaction.atomic():
                if make_default:
                    Address.objects.filter(user=user, is_default=True).update(is_default=False)
                return Address.objects.create(user=user, is_default=make_default, **data)
        except IntegrityError:
            return Address.objects.create(user=user, is_default=False, **data)


def update_address(address: Address, **data) -> Address:
    make_default = data.get("is_default", address.is_default)
    with transaction.atomic():
        if make_default:
            Address.objects.filter(user=address.user, is_default=True).exclude(pk=address.pk).update(is_default=False)
        for field, value in data.items():
            setattr(address, field, value)
        address.is_default = make_default
        address.save()
    return address


def delete_address(address: Address) -> None:
    user = address.user
    was_default = address.is_default
    address.delete()
    if was_default:
        replacement = Address.objects.filter(user=user).order_by("created_at").first()
        if replacement is not None:
            replacement.is_default = True
            replacement.save(update_fields=["is_default", "updated_at"])


def _code_matches(factor: MfaFactor, code: str) -> bool:
    secret = decrypt_secret(factor.secret_encrypted)
    return bool(pyotp.TOTP(secret).verify((code or "").replace(" ", ""), valid_window=1))


def _issue_one_time_token(user: User, purpose: str, *, hours: int) -> str:
    raw = new_raw_token()
    OneTimeToken.objects.create(
        user=user,
        purpose=purpose,
        token_hash=hash_token(raw),
        expires_at=timezone.now() + timedelta(hours=hours),
    )
    return raw


def _consume_token(raw_token: str, purpose: str) -> OneTimeToken | None:
    if not raw_token:
        return None
    with transaction.atomic():
        token = (
            OneTimeToken.objects.select_for_update()
            .filter(
                token_hash=hash_token(raw_token),
                purpose=purpose,
                used_at__isnull=True,
                expires_at__gt=timezone.now(),
            )
            .select_related("user")
            .first()
        )
        if token is None:
            return None
        token.used_at = timezone.now()
        token.save(update_fields=["used_at", "updated_at"])
        return token


def _send_verification_email(user: User, raw: str) -> None:
    link = f"{settings.WEB_ORIGIN}/verify-account?token={raw}"
    send_mail(
        "Verify your MediSource GH email",
        (
            "Confirm this address to finish setting up your MediSource GH account.\n\n"
            f"{link}\n\n"
            "This link expires in 24 hours."
        ),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

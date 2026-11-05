from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from common.crypto import decrypt, encrypt
from modules.identity.models import AgencyRole, User

import pyotp


def issue_token_pair(user: User) -> tuple[str, str]:
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def owner_must_enroll(user: User) -> bool:
    return (
        settings.MFA_REQUIRED_FOR_AGENCY_OWNER
        and user.role == AgencyRole.AGENCY_OWNER
        and not user.mfa_enabled
    )


def begin_enrollment(user: User) -> str:
    secret = pyotp.random_base32()
    user.mfa_secret = encrypt(secret)
    user.mfa_enabled = False
    user.save(update_fields=["mfa_secret", "mfa_enabled", "updated_at"])
    return pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="SRAJ NOVA")


def confirm_enrollment(user: User, code: str) -> bool:
    if not user.mfa_secret:
        return False
    if not pyotp.TOTP(decrypt(user.mfa_secret)).verify(code, valid_window=1):
        return False
    user.mfa_enabled = True
    user.save(update_fields=["mfa_enabled", "updated_at"])
    return True


def verify_totp(user: User, code: str) -> bool:
    if not user.mfa_enabled or not user.mfa_secret:
        return False
    return pyotp.TOTP(decrypt(user.mfa_secret)).verify(code, valid_window=1)


def authenticate_user(*, email: str, password: str) -> User | None:
    return authenticate(username=email, password=password)

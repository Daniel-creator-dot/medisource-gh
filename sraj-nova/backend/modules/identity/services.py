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


ROLE_LABELS = {
    AgencyRole.AGENCY_OWNER: "Agency owner",
    AgencyRole.AGENCY_OPERATIONS: "Agency operations",
    AgencyRole.AGENCY_FINANCE: "Agency finance",
    AgencyRole.CLIENT_USER: "Client user",
    AgencyRole.EMPLOYEE: "Employee",
}

ROLE_OPENS = {
    AgencyRole.AGENCY_OWNER: ["Command", "Departments", "Floor", "Actions", "Coverage", "HR", "Recruitment", "People", "Clients", "Finance", "Books", "Tax", "Agency", "Roles", "Settings"],
    AgencyRole.AGENCY_OPERATIONS: ["Command", "Departments", "Floor", "Actions", "Coverage", "HR", "Recruitment", "People", "Clients", "Finance", "Books", "Tax", "Agency", "Settings"],
    AgencyRole.AGENCY_FINANCE: ["Command", "Departments", "Floor", "Actions", "Coverage", "HR", "Recruitment", "People", "Clients", "Finance", "Books", "Tax", "Agency", "Settings"],
    AgencyRole.CLIENT_USER: ["Command", "Departments", "Floor", "Actions", "Coverage", "People", "Clients", "Finance", "Tax", "Settings"],
    AgencyRole.EMPLOYEE: ["My record", "Tax", "Settings"],
}


class RoleAssignmentError(Exception):
    def __init__(self, message: str):
        self.message = message


def assignable_roles(user: User) -> list[str]:
    choices = [AgencyRole.AGENCY_OWNER, AgencyRole.AGENCY_OPERATIONS, AgencyRole.AGENCY_FINANCE]
    if user.client_id:
        choices.append(AgencyRole.CLIENT_USER)
    if user.employee_id:
        choices.append(AgencyRole.EMPLOYEE)
    return choices


def assign_role(target: User, role: str) -> None:
    if role not in ROLE_LABELS:
        raise RoleAssignmentError("Choose one of the five roles.")
    if role not in assignable_roles(target):
        if role == AgencyRole.CLIENT_USER:
            raise RoleAssignmentError("This account is not linked to one client, so it cannot be a client user.")
        raise RoleAssignmentError("This account has no worker record, so it cannot be an employee.")
    if target.role == AgencyRole.AGENCY_OWNER and role != AgencyRole.AGENCY_OWNER:
        another_owner = User.objects.filter(role=AgencyRole.AGENCY_OWNER, is_active=True).exclude(pk=target.pk).exists()
        if not another_owner:
            raise RoleAssignmentError("This is the only agency owner. Give another account that role first.")
    target.role = role
    target.save(update_fields=["role", "updated_at"])


def change_password(user: User, current: str, new: str) -> None:
    if not user.check_password(current):
        raise RoleAssignmentError("The current password is not correct.")
    if len(new) < 8:
        raise RoleAssignmentError("Use at least 8 characters.")
    user.set_password(new)
    user.save(update_fields=["password", "updated_at"])


def account_settings(user: User) -> dict:
    return {
        "email": user.email,
        "name": user.get_full_name(),
        "role": user.role,
        "role_label": ROLE_LABELS[user.role],
        "opens": ROLE_OPENS[user.role],
        "mfa_enabled": user.mfa_enabled,
        "mfa_required_for_owner": settings.MFA_REQUIRED_FOR_AGENCY_OWNER,
        "late_grace_minutes": settings.LATE_GRACE_MINUTES,
        "min_rest_hours": settings.MIN_REST_HOURS,
        "can_manage_roles": user.role == AgencyRole.AGENCY_OWNER,
        "can_manage_hr": user.role in {AgencyRole.AGENCY_OWNER, AgencyRole.AGENCY_OPERATIONS, AgencyRole.AGENCY_FINANCE},
    }

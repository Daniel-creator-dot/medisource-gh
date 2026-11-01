import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import UUIDTimeStampedModel
from modules.identity.managers import UserManager


class PlatformRole(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    SUPPLIER = "supplier", "Supplier"
    FACILITY = "facility", "Facility"
    PROFESSIONAL = "professional", "Professional"
    PLATFORM_ADMIN = "platform_admin", "Platform admin"
    FINANCE_OFFICER = "finance_officer", "Finance officer"


PRIVILEGED_ROLES = {PlatformRole.PLATFORM_ADMIN, PlatformRole.FINANCE_OFFICER}


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    platform_role = models.CharField(
        max_length=32,
        choices=PlatformRole.choices,
        default=PlatformRole.CUSTOMER,
    )
    email_verified = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)
    is_demo_account = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    class Meta:
        indexes = [models.Index(fields=["platform_role"])]

    def __str__(self) -> str:
        return self.email


class OneTimeToken(UUIDTimeStampedModel):
    class Purpose(models.TextChoices):
        EMAIL_VERIFY = "email_verify", "Email verification"
        PASSWORD_RESET = "password_reset", "Password reset"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="one_time_tokens")
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["purpose", "expires_at"])]


class MfaFactor(UUIDTimeStampedModel):
    class Method(models.TextChoices):
        TOTP = "totp", "Authenticator app"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_factors")
    method = models.CharField(max_length=16, choices=Method.choices, default=Method.TOTP)
    secret_encrypted = models.TextField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "method"],
                condition=models.Q(is_active=True),
                name="one_active_mfa_factor_per_method",
            )
        ]


class Address(UUIDTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=40)
    recipient_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default="GH")
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="one_default_address_per_user",
            )
        ]
        ordering = ["-is_default", "label"]

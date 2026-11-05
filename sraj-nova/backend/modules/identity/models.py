from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common.models import UUIDModel


class AgencyRole(models.TextChoices):
    AGENCY_OWNER = "agency_owner", "Agency owner"
    AGENCY_OPERATIONS = "agency_operations", "Agency operations"
    AGENCY_FINANCE = "agency_finance", "Agency finance"
    CLIENT_USER = "client_user", "Client user"
    EMPLOYEE = "employee", "Employee"


AGENCY_ROLES = (
    AgencyRole.AGENCY_OWNER,
    AgencyRole.AGENCY_OPERATIONS,
    AgencyRole.AGENCY_FINANCE,
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", AgencyRole.AGENCY_OWNER)
        return self.create_user(email, password, **extra)


class User(UUIDModel, AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=AgencyRole.choices)
    client = models.ForeignKey(
        "organization.Client",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="users",
    )
    employee = models.OneToOneField(
        "workforce.Employee",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="account",
    )
    mfa_secret = models.TextField(blank=True)
    mfa_enabled = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self) -> str:
        return self.email

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from modules.identity.models import Address, MfaFactor, OneTimeToken, User


class EmailUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class EmailUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "platform_role",
        "email_verified",
        "mfa_enabled",
        "is_staff",
    )
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profile",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "platform_role",
                    "email_verified",
                    "mfa_enabled",
                    "is_demo_account",
                )
            },
        ),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "platform_role", "is_staff")}),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("label", "user", "city", "region", "is_default")
    search_fields = ("user__email", "city", "line1")


@admin.register(OneTimeToken)
class OneTimeTokenAdmin(admin.ModelAdmin):
    list_display = ("purpose", "user", "expires_at", "used_at")
    readonly_fields = ("token_hash",)


@admin.register(MfaFactor)
class MfaFactorAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "is_active", "confirmed_at")
    exclude = ("secret_encrypted",)

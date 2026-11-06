from django.urls import path

from modules.identity.views import (
    AccessUsersView,
    AccountSettingsView,
    AssignRoleView,
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    MfaConfirmView,
    MfaEnrollView,
    MfaVerifyView,
    PasswordView,
)

urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="csrf"),
    path("login/", LoginView.as_view(), name="login"),
    path("mfa/verify/", MfaVerifyView.as_view(), name="mfa-verify"),
    path("mfa/enroll/", MfaEnrollView.as_view(), name="mfa-enroll"),
    path("mfa/confirm/", MfaConfirmView.as_view(), name="mfa-confirm"),
    path("me/", MeView.as_view(), name="me"),
    path("settings/", AccountSettingsView.as_view(), name="account-settings"),
    path("password/", PasswordView.as_view(), name="password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/", AccessUsersView.as_view(), name="access-users"),
    path("users/<uuid:user_id>/role/", AssignRoleView.as_view(), name="assign-role"),
]

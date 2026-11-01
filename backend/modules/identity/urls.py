from django.urls import path

from modules.identity.views import (
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    MfaConfirmView,
    MfaEnrollView,
    MfaVerifyView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
    ResendVerificationView,
    VerifyEmailView,
)

urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="auth-resend-verification"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("mfa/verify/", MfaVerifyView.as_view(), name="auth-mfa-verify"),
    path("mfa/enroll/", MfaEnrollView.as_view(), name="auth-mfa-enroll"),
    path("mfa/confirm/", MfaConfirmView.as_view(), name="auth-mfa-confirm"),
]

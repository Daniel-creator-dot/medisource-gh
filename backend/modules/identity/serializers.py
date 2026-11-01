from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from modules.identity.models import Address, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "platform_role",
            "email_verified",
            "mfa_enabled",
            "is_demo_account",
        ]
        read_only_fields = [
            "id",
            "email",
            "platform_role",
            "email_verified",
            "mfa_enabled",
            "is_demo_account",
        ]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class TokenCodeSerializer(serializers.Serializer):
    token = serializers.CharField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class MfaCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    mfa_token = serializers.CharField(required=False, allow_blank=True)
    enrollment_token = serializers.CharField(required=False, allow_blank=True)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "recipient_name",
            "phone_number",
            "line1",
            "line2",
            "city",
            "region",
            "postal_code",
            "country",
            "is_default",
        ]
        read_only_fields = ["id"]

    def validate_country(self, value: str) -> str:
        country = value.strip().upper()
        if len(country) != 2 or not country.isalpha():
            raise serializers.ValidationError("Use a two-letter country code.")
        return country

from rest_framework import serializers

from modules.identity.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=8)


class UserSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "mfa_enabled", "is_demo", "client_id", "employee_id"]

    def get_client_id(self, obj: User):
        return str(obj.client_id) if obj.client_id else None

    def get_employee_id(self, obj: User):
        return str(obj.employee_id) if obj.employee_id else None

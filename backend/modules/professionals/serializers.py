from rest_framework import serializers

from modules.professionals.models import ProfessionRole, ProfessionalProfile


class ProfessionRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionRole
        fields = ["id", "name", "slug", "description"]


class ProfessionalCardSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name")
    role_slug = serializers.CharField(source="role.slug")

    class Meta:
        model = ProfessionalProfile
        fields = [
            "id",
            "display_name",
            "slug",
            "city",
            "region",
            "summary",
            "role_name",
            "role_slug",
            "verification_status",
            "credential_expires_on",
        ]

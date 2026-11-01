from rest_framework import serializers

from modules.notifications.models import ContactInquiry, Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "is_read", "created_at"]
        read_only_fields = fields


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "organization_name", "topic", "message"]

    def validate_message(self, value: str) -> str:
        message = value.strip()
        if len(message) < 20:
            raise serializers.ValidationError("Write at least 20 characters so the team can help.")
        if len(message) > 2000:
            raise serializers.ValidationError("Keep the message under 2000 characters.")
        return message

    def validate_name(self, value: str) -> str:
        name = value.strip()
        if len(name) < 2:
            raise serializers.ValidationError("Enter your name.")
        return name

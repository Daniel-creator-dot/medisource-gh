from django.contrib import admin

from modules.notifications.models import ContactInquiry, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "topic", "created_at")
    search_fields = ("email", "name", "organization_name")
    readonly_fields = ("name", "email", "organization_name", "topic", "message", "ip_address", "created_at")

from django.contrib import admin

from modules.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "resource_type", "actor", "ip_address")
    list_filter = ("action", "resource_type")
    search_fields = ("action", "resource_id")
    readonly_fields = (
        "actor",
        "action",
        "resource_type",
        "resource_id",
        "metadata",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

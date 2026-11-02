from django.contrib import admin

from modules.professionals.models import ProfessionRole, ProfessionalProfile


@admin.register(ProfessionRole)
class ProfessionRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role", "region", "verification_status", "is_demo", "credential_expires_on")
    list_filter = ("verification_status", "is_demo", "region")
    search_fields = ("display_name", "city")

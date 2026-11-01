from django.urls import path

from modules.organizations.views import OrganizationDetailView

urlpatterns = [
    path("organizations/<uuid:organization_id>/", OrganizationDetailView.as_view(), name="organization-detail"),
]

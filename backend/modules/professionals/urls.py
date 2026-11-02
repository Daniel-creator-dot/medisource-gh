from django.urls import path

from modules.professionals.views import ProfessionRoleListView, ProfessionalListView

urlpatterns = [
    path("", ProfessionalListView.as_view(), name="professional-list"),
    path("roles/", ProfessionRoleListView.as_view(), name="professional-roles"),
]

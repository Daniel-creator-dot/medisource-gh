from django.urls import path

from modules.organization.views import AgencyView, ClientDetailView, ClientListView, CommandCenterView

urlpatterns = [
    path("agency/", AgencyView.as_view(), name="agency"),
    path("clients/", ClientListView.as_view(), name="clients"),
    path("clients/<slug:slug>/", ClientDetailView.as_view(), name="client-detail"),
    path("command-center/", CommandCenterView.as_view(), name="command-center"),
]

from django.urls import path

from modules.identity.views import AddressDetailView, AddressListCreateView, MembershipListView

urlpatterns = [
    path("account/addresses/", AddressListCreateView.as_view(), name="address-list"),
    path("account/addresses/<uuid:address_id>/", AddressDetailView.as_view(), name="address-detail"),
    path("account/memberships/", MembershipListView.as_view(), name="membership-list"),
]

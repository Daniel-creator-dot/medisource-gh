from django.urls import path

from modules.catalog.views import (
    CategoryListView,
    ProductDetailView,
    ProductListView,
    SupplierDetailView,
    SupplierInternalView,
    SupplierListView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("suppliers/", SupplierListView.as_view(), name="supplier-list"),
    path("suppliers/<slug:slug>/", SupplierDetailView.as_view(), name="supplier-detail"),
    path("suppliers/<slug:slug>/internal/", SupplierInternalView.as_view(), name="supplier-internal"),
]

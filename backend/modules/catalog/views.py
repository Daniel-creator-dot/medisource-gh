from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import ok
from common.pagination import EnvelopePagination
from modules.catalog.models import Supplier
from modules.catalog.serializers import (
    CategorySerializer,
    ProductCardSerializer,
    ProductDetailSerializer,
    SupplierCardSerializer,
    SupplierDetailSerializer,
)
from modules.catalog.services import (
    filter_products,
    get_public_product,
    get_public_supplier,
    public_categories,
    public_suppliers,
)
from modules.organizations.services import active_membership


class CategoryListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return ok(CategorySerializer(public_categories(), many=True).data)


class ProductListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = filter_products(request.query_params)
        paginator = EnvelopePagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(ProductCardSerializer(page, many=True).data)


class ProductDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug):
        return ok(ProductDetailSerializer(get_public_product(slug)).data)


class SupplierListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = public_suppliers()
        paginator = EnvelopePagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(SupplierCardSerializer(page, many=True).data)


class SupplierDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, slug):
        return ok(SupplierDetailSerializer(get_public_supplier(slug)).data)


class SupplierInternalView(APIView):
    def get(self, request, slug):
        supplier = Supplier.objects.filter(slug=slug).select_related("organization").first()
        if supplier is None or active_membership(request.user, supplier.organization) is None:
            raise Http404()
        return ok({"id": str(supplier.id), "internal_notes": supplier.internal_notes})

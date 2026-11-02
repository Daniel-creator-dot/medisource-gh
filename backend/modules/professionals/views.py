from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import ok
from common.pagination import EnvelopePagination
from modules.professionals.constants import DIRECTORY_NOTICE, GHANA_REGIONS
from modules.professionals.models import ProfessionRole
from modules.professionals.serializers import ProfessionRoleSerializer, ProfessionalCardSerializer
from modules.professionals.services import public_professionals


class ProfessionRoleListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return ok(
            {
                "roles": ProfessionRoleSerializer(ProfessionRole.objects.all(), many=True).data,
                "regions": GHANA_REGIONS,
                "notice": DIRECTORY_NOTICE,
            }
        )


class ProfessionalListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = public_professionals(request.query_params)
        paginator = EnvelopePagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(ProfessionalCardSerializer(page, many=True).data)

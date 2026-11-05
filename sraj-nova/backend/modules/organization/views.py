from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.api import ok
from modules.identity.models import AGENCY_ROLES, AgencyRole
from modules.operations.services import command_center, scoped_clients
from modules.organization.models import Agency, Client


class AgencyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in AGENCY_ROLES:
            raise PermissionDenied()
        agency = Agency.objects.first()
        if agency is None:
            raise NotFound()
        return ok(
            {
                "id": str(agency.id),
                "legal_name": agency.legal_name,
                "trading_name": agency.trading_name,
                "country": agency.country,
                "currency": agency.currency,
                "timezone": agency.timezone,
                "role": "Workforce outsourcing agency. Client factories are external organizations.",
            }
        )


class ClientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        clients = scoped_clients(request.user)
        return ok(
            [
                {
                    "id": str(client.id),
                    "legal_name": client.legal_name,
                    "slug": client.slug,
                    "sector": client.sector,
                    "status": client.status,
                    "is_demo": client.is_demo,
                    "demo_label": client.demo_label,
                    "site_count": client.sites.count(),
                    "deployed_workers": client.deployments.filter(is_current=True).count(),
                }
                for client in clients
            ]
        )


class ClientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        client = scoped_clients(request.user).filter(slug=slug).first()
        if client is None:
            raise NotFound()
        return ok(
            {
                "id": str(client.id),
                "legal_name": client.legal_name,
                "slug": client.slug,
                "sector": client.sector,
                "status": client.status,
                "is_demo": client.is_demo,
                "demo_label": client.demo_label,
                "sites": [
                    {
                        "id": str(site.id),
                        "name": site.name,
                        "city": site.city,
                        "region": site.region,
                        "departments": [department.name for department in site.departments.all()],
                    }
                    for site in client.sites.prefetch_related("departments")
                ],
            }
        )


class CommandCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == AgencyRole.EMPLOYEE:
            raise PermissionDenied()
        return ok(command_center(request.user))

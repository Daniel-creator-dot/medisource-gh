from django.http import Http404
from rest_framework.views import APIView

from common.api import ok
from modules.audit.services import record_audit
from modules.identity.models import PlatformRole
from modules.organizations.models import Organization
from modules.organizations.serializers import OrganizationSerializer
from modules.organizations.services import active_membership


class OrganizationDetailView(APIView):
    def get(self, request, organization_id):
        organization = Organization.objects.filter(pk=organization_id).first()
        if organization is None:
            raise Http404()
        if active_membership(request.user, organization):
            return ok(OrganizationSerializer(organization).data)
        if request.user.platform_role == PlatformRole.PLATFORM_ADMIN:
            record_audit(
                actor=request.user,
                action="organization.admin_view",
                resource_type="organization",
                resource_id=organization.id,
                request=request,
            )
            return ok(OrganizationSerializer(organization).data)
        raise Http404()

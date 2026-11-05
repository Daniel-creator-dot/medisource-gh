from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.health import HealthView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/auth/", include("modules.identity.urls")),
    path("api/v1/", include("modules.organization.urls")),
    path("api/v1/", include("modules.workforce.urls")),
    path("api/v1/", include("modules.operations.urls")),
    path("api/v1/", include("modules.finance.urls")),
]

admin.site.site_header = "SRAJ NOVA technical admin"

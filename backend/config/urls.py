from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from common.health import ApiRootView, HealthView

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("django-admin/", admin.site.urls),
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/auth/", include("modules.identity.urls")),
    path("api/v1/", include("modules.identity.account_urls")),
    path("api/v1/", include("modules.organizations.urls")),
    path("api/v1/catalog/", include("modules.catalog.urls")),
    path("api/v1/", include("modules.notifications.urls")),
]

admin.site.site_header = "MediSource GH technical admin"
admin.site.site_title = "MediSource GH"

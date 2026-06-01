"""Root URL configuration."""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

api_v1 = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.patients.urls")),
    path("", include("apps.appointments.urls")),
    path("", include("apps.visits.urls")),
    path("", include("apps.dental_charts.urls")),
    path("", include("apps.treatments.urls")),
    path("", include("apps.prescriptions.urls")),
    path("", include("apps.billing.urls")),
    path("", include("apps.expenses.urls")),
    path("", include("apps.inventory.urls")),
    path("", include("apps.documents.urls")),
    path("", include("apps.followups.urls")),
    path("", include("apps.reports.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.audit.urls")),
]

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include(api_v1)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

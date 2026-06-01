from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import dashboard_summary, ClinicInfoViewSet

router = DefaultRouter()
router.register("settings", ClinicInfoViewSet, basename="settings")

urlpatterns = [
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
] + router.urls

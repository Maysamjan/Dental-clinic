from django.utils import timezone
from rest_framework import viewsets

from apps.core.permissions import HasModulePermission
from .models import TreatmentCatalog, TreatmentPlan, TreatmentStage, Treatment
from .serializers import (
    TreatmentCatalogSerializer, TreatmentPlanSerializer,
    TreatmentStageSerializer, TreatmentSerializer,
)


class TreatmentCatalogViewSet(viewsets.ModelViewSet):
    module = "treatments"
    permission_classes = [HasModulePermission]
    queryset = TreatmentCatalog.objects.all()
    serializer_class = TreatmentCatalogSerializer
    search_fields = ["name", "code", "category"]
    filterset_fields = ["category", "is_active"]


class TreatmentPlanViewSet(viewsets.ModelViewSet):
    module = "treatments"
    permission_classes = [HasModulePermission]
    queryset = TreatmentPlan.objects.select_related(
        "patient", "doctor", "doctor__user"
    ).prefetch_related("stages__treatments")
    serializer_class = TreatmentPlanSerializer
    filterset_fields = ["patient", "doctor", "status"]
    search_fields = ["title", "patient__full_name"]


class TreatmentStageViewSet(viewsets.ModelViewSet):
    module = "treatments"
    permission_classes = [HasModulePermission]
    queryset = TreatmentStage.objects.select_related("plan")
    serializer_class = TreatmentStageSerializer
    filterset_fields = ["plan", "status"]


class TreatmentViewSet(viewsets.ModelViewSet):
    module = "treatments"
    permission_classes = [HasModulePermission]
    queryset = Treatment.objects.select_related(
        "stage__plan", "catalog_item", "tooth", "visit"
    )
    serializer_class = TreatmentSerializer
    filterset_fields = ["stage", "visit", "tooth", "status"]

    def perform_create(self, serializer):
        treatment = serializer.save()
        self._after_change(treatment)

    def perform_update(self, serializer):
        treatment = serializer.save()
        if treatment.status == "COMPLETED" and not treatment.performed_at:
            treatment.performed_at = timezone.now()
            treatment.save(update_fields=["performed_at"])
        self._after_change(treatment)

    def _after_change(self, treatment):
        if treatment.stage_id and treatment.stage.plan_id:
            treatment.stage.plan.recompute_progress()

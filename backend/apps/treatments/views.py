from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission, user_has_perm
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

    @action(detail=True, methods=["post"], url_path="generate-invoice")
    def generate_invoice(self, request, pk=None):
        """Create a draft invoice from this plan's not-yet-invoiced treatments.

        By default only COMPLETED treatments are billed; pass {"all": true}
        to bill every treatment in the plan.
        """
        if not user_has_perm(request.user, "billing.add"):
            return Response({"detail": "Billing permission required."}, status=403)

        from apps.billing.models import Invoice, InvoiceItem

        plan = self.get_object()
        bill_all = request.data.get("all", False)
        treatments = Treatment.objects.filter(stage__plan=plan).select_related("catalog_item")
        if not bill_all:
            treatments = treatments.filter(status="COMPLETED")

        already = set(
            InvoiceItem.objects.filter(treatment__in=treatments)
            .values_list("treatment_id", flat=True)
        )
        billable = [t for t in treatments if t.id not in already and t.total > 0]
        if not billable:
            return Response(
                {"detail": "No un-invoiced billable treatments found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice = Invoice.objects.create(
            patient=plan.patient,
            issued_by=request.user if request.user.is_authenticated else None,
            notes=f"Generated from treatment plan: {plan.title}",
        )
        for t in billable:
            label = t.description or (t.catalog_item.name if t.catalog_item else "Treatment")
            if t.tooth_id:
                label = f"{label} (tooth {t.tooth.fdi_number})"
            InvoiceItem.objects.create(
                invoice=invoice, treatment=t, description=label,
                quantity=t.quantity, unit_price=t.unit_price,
            )
        invoice.recompute()

        from apps.billing.serializers import InvoiceSerializer
        return Response(
            InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED
        )


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

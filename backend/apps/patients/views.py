from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer


class PatientViewSet(viewsets.ModelViewSet):
    module = "patients"
    permission_classes = [HasModulePermission]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    search_fields = ["full_name", "code", "phone"]
    filterset_fields = ["gender", "is_archived"]
    ordering_fields = ["full_name", "registration_date", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        return PatientSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # By default hide archived patients unless explicitly requested.
        if self.action == "list" and self.request.query_params.get("is_archived") is None:
            qs = qs.filter(is_archived=False)
        return qs

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        patient = self.get_object()
        patient.is_archived = True
        patient.save(update_fields=["is_archived"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        patient = self.get_object()
        patient.is_archived = False
        patient.save(update_fields=["is_archived"])
        return Response({"status": "restored"})

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Aggregated clinical & financial history for the patient."""
        from decimal import Decimal

        from django.db.models import Sum

        patient = self.get_object()
        from apps.visits.models import Visit
        from apps.prescriptions.models import Prescription
        from apps.billing.models import Invoice, Payment
        from apps.appointments.models import Appointment
        from apps.treatments.models import TreatmentPlan
        from apps.documents.models import Document
        from apps.followups.models import FollowUp

        from apps.visits.serializers import VisitSerializer
        from apps.prescriptions.serializers import PrescriptionSerializer
        from apps.billing.serializers import InvoiceSerializer, PaymentSerializer
        from apps.appointments.serializers import AppointmentSerializer
        from apps.treatments.serializers import TreatmentPlanSerializer
        from apps.documents.serializers import DocumentSerializer
        from apps.followups.serializers import FollowUpSerializer

        ctx = self.get_serializer_context()
        zero = Decimal("0.00")
        invoices = Invoice.objects.filter(patient=patient)
        payments = Payment.objects.filter(invoice__patient=patient).select_related("invoice")

        totals = invoices.aggregate(billed=Sum("total"), paid=Sum("paid_amount"),
                                    balance=Sum("balance"))

        data = {
            "patient": PatientSerializer(patient, context=ctx).data,
            "financial_summary": {
                "total_billed": totals["billed"] or zero,
                "total_paid": totals["paid"] or zero,
                "outstanding_balance": totals["balance"] or zero,
            },
            "appointments": AppointmentSerializer(
                Appointment.objects.filter(patient=patient).select_related("doctor__user")[:50], many=True
            ).data,
            "visits": VisitSerializer(
                Visit.objects.filter(patient=patient).select_related("doctor__user")[:50], many=True
            ).data,
            "treatment_plans": TreatmentPlanSerializer(
                TreatmentPlan.objects.filter(patient=patient).prefetch_related("stages__treatments")[:50], many=True
            ).data,
            "prescriptions": PrescriptionSerializer(
                Prescription.objects.filter(patient=patient).prefetch_related("items")[:50], many=True
            ).data,
            "invoices": InvoiceSerializer(invoices.prefetch_related("items", "payments")[:50], many=True).data,
            "payments": PaymentSerializer(payments[:50], many=True).data,
            "documents": DocumentSerializer(
                Document.objects.filter(patient=patient)[:50], many=True, context=ctx
            ).data,
            "follow_ups": FollowUpSerializer(
                FollowUp.objects.filter(patient=patient)[:50], many=True
            ).data,
        }
        return Response(data)

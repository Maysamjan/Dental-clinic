from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.core.permissions import HasModulePermission
from apps.core.pdf import build_pdf
from .models import Prescription
from .serializers import PrescriptionSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    module = "prescriptions"
    permission_classes = [HasModulePermission]
    queryset = Prescription.objects.select_related(
        "patient", "doctor", "doctor__user"
    ).prefetch_related("items")
    serializer_class = PrescriptionSerializer
    filterset_fields = ["patient", "doctor", "visit"]
    search_fields = ["patient__full_name", "items__medication"]

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        rx = self.get_object()
        intro = [
            f"<b>Patient:</b> {rx.patient.full_name} ({rx.patient.code})",
            f"<b>Doctor:</b> {rx.doctor.user.full_name if rx.doctor else '-'}",
            f"<b>Date:</b> {rx.created_at:%Y-%m-%d}",
        ]
        rows = [
            [i.medication, i.dosage, i.frequency, i.duration, i.notes]
            for i in rx.items.all()
        ]
        pdf = build_pdf(
            "Prescription",
            intro,
            ["Medication", "Dosage", "Frequency", "Duration", "Notes"],
            rows,
            footer=rx.notes,
        )
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="prescription-{rx.id}.pdf"'
        return resp

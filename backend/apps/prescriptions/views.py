from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.core.permissions import HasModulePermission
from apps.core.pdf import build_branded_pdf
from .models import Prescription, PrescriptionTemplate
from .serializers import PrescriptionSerializer, PrescriptionTemplateSerializer


class PrescriptionTemplateViewSet(viewsets.ModelViewSet):
    module = "prescriptions"
    permission_classes = [HasModulePermission]
    queryset = PrescriptionTemplate.objects.all()
    serializer_class = PrescriptionTemplateSerializer
    search_fields = ["name"]


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
        patient = rx.patient
        age = f"{patient.age} yrs" if patient.age is not None else "—"
        intro = [
            f"<b>Patient:</b> {patient.full_name} ({patient.code}) &nbsp;&nbsp; "
            f"<b>Age/Sex:</b> {age} / {patient.get_gender_display()}",
            f"<b>Date:</b> {rx.created_at:%Y-%m-%d}",
        ]
        rows = [
            [f"<b>{i.medication}</b>", i.dosage, i.frequency, i.duration, i.notes]
            for i in rx.items.all()
        ]

        # Doctor signature block.
        signature_line = ""
        signature_image = None
        if rx.doctor:
            signature_line = f"Dr. {rx.doctor.user.full_name}"
            if rx.doctor.license_number:
                signature_line += f"<br/>Lic: {rx.doctor.license_number}"
            if rx.doctor.specialization:
                signature_line += f"<br/>{rx.doctor.specialization}"
            if getattr(rx.doctor, "signature", None) and rx.doctor.signature:
                try:
                    signature_image = rx.doctor.signature.path
                except Exception:
                    signature_image = None

        try:
            from apps.dashboard.models import ClinicInfo
            footer = ClinicInfo.load().prescription_footer or ""
        except Exception:
            footer = ""
        if rx.notes:
            footer = (footer + "<br/>" if footer else "") + f"Notes: {rx.notes}"

        pdf = build_branded_pdf(
            "℞ Prescription",
            intro,
            ["Medication", "Dosage", "Frequency", "Duration", "Notes"],
            rows,
            footer=footer or None,
            signature=signature_line or None,
            signature_image=signature_image,
        )
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="prescription-{rx.id}.pdf"'
        return resp

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient


class Document(TimeStampedModel):
    TYPES = [
        ("PHOTO", "Patient Photo"),
        ("XRAY", "X-Ray"),
        ("OPG", "OPG Image"),
        ("PDF", "PDF Document"),
        ("LAB", "Laboratory File"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="documents"
    )
    type = models.CharField(max_length=6, choices=TYPES, default="PHOTO")
    title = models.CharField(max_length=150, blank=True)
    file = models.FileField(upload_to="patients/documents/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.get_type_display()} - {self.patient.full_name}"

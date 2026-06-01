from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient

TOOTH_STATUS = [
    ("HEALTHY", "Healthy"),
    ("CARIES", "Caries"),
    ("FILLING", "Filling"),
    ("ROOT_CANAL", "Root Canal"),
    ("CROWN", "Crown"),
    ("BRIDGE", "Bridge"),
    ("IMPLANT", "Implant"),
    ("EXTRACTION", "Extraction"),
    ("ORTHODONTIC", "Orthodontic Treatment"),
]


class DentalChart(TimeStampedModel):
    DENTITION = [("ADULT", "Adult (32)"), ("CHILD", "Child (20)")]

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="dental_chart"
    )
    dentition = models.CharField(max_length=6, choices=DENTITION, default="ADULT")

    def __str__(self):
        return f"Chart for {self.patient.full_name}"


class Tooth(models.Model):
    chart = models.ForeignKey(DentalChart, on_delete=models.CASCADE, related_name="teeth")
    fdi_number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=12, choices=TOOTH_STATUS, default="HEALTHY")

    class Meta:
        ordering = ["fdi_number"]
        unique_together = ("chart", "fdi_number")

    def __str__(self):
        return f"Tooth {self.fdi_number} ({self.status})"


class ToothCondition(TimeStampedModel):
    """Per-tooth history entry — what was found/done and when."""

    SURFACES = [
        ("M", "Mesial"), ("D", "Distal"), ("O", "Occlusal"),
        ("B", "Buccal"), ("L", "Lingual"), ("", "Whole tooth"),
    ]

    tooth = models.ForeignKey(Tooth, on_delete=models.CASCADE, related_name="conditions")
    condition = models.CharField(max_length=12, choices=TOOTH_STATUS)
    surface = models.CharField(max_length=1, choices=SURFACES, blank=True)
    note = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    treatment = models.ForeignKey(
        "treatments.Treatment", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="tooth_conditions",
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ["-created_at"]

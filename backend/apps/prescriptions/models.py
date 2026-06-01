from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.accounts.models import Doctor


class Prescription(TimeStampedModel):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="prescriptions"
    )
    doctor = models.ForeignKey(
        Doctor, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="prescriptions",
    )
    visit = models.ForeignKey(
        "visits.Visit", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="prescriptions",
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Prescription #{self.id} - {self.patient.full_name}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="items"
    )
    medication = models.CharField(max_length=150)
    dosage = models.CharField(max_length=80, blank=True)
    frequency = models.CharField(max_length=80, blank=True)
    duration = models.CharField(max_length=80, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.medication

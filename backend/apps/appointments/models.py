from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.accounts.models import Doctor


class Appointment(TimeStampedModel):
    STATUS = [
        ("SCHEDULED", "Scheduled"),
        ("CONFIRMED", "Confirmed"),
        ("ARRIVED", "Arrived"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("NO_SHOW", "No Show"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="appointments",
    )
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="SCHEDULED")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["start"]
        indexes = [models.Index(fields=["start"]), models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.patient.full_name} @ {self.start:%Y-%m-%d %H:%M}"

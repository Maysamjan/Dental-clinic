from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient


class FollowUp(TimeStampedModel):
    TYPES = [("VISIT", "Next Visit"), ("PAYMENT", "Outstanding Payment")]
    STATUS = [("PENDING", "Pending"), ("DONE", "Done"), ("CANCELLED", "Cancelled")]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="follow_ups"
    )
    type = models.CharField(max_length=8, choices=TYPES, default="VISIT")
    due_date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="PENDING")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta(TimeStampedModel.Meta):
        ordering = ["due_date"]
        indexes = [models.Index(fields=["due_date", "status"])]

    def __str__(self):
        return f"{self.get_type_display()} for {self.patient.full_name} on {self.due_date}"

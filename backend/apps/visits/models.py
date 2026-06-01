from datetime import date

from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.accounts.models import Doctor
from apps.appointments.models import Appointment


class Visit(TimeStampedModel):
    """A clinical encounter. Also drives the live reception/doctor queue."""

    WORKFLOW = [
        ("WAITING", "Waiting"),
        ("IN_CONSULTATION", "In Consultation"),
        ("TREATMENT_IN_PROGRESS", "Treatment In Progress"),
        ("COMPLETED", "Completed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    doctor = models.ForeignKey(
        Doctor, null=True, blank=True, on_delete=models.SET_NULL, related_name="visits"
    )
    appointment = models.OneToOneField(
        Appointment, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="visit",
    )

    visit_date = models.DateField(default=date.today)
    visit_time = models.TimeField(default=timezone.localtime)

    chief_complaint = models.TextField(blank=True)
    clinical_findings = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Live workflow / queue
    queue_number = models.PositiveIntegerField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    workflow_status = models.CharField(
        max_length=24, choices=WORKFLOW, default="WAITING"
    )

    class Meta:
        ordering = ["-visit_date", "queue_number"]
        indexes = [
            models.Index(fields=["visit_date"]),
            models.Index(fields=["workflow_status"]),
        ]

    def __str__(self):
        return f"Visit #{self.id} - {self.patient.full_name}"

    @classmethod
    def next_queue_number(cls, day=None):
        day = day or date.today()
        last = cls.objects.filter(visit_date=day).aggregate(
            m=models.Max("queue_number")
        )["m"]
        return (last or 0) + 1

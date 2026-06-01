from decimal import Decimal

from django.db import models

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.accounts.models import Doctor


class TreatmentCatalog(TimeStampedModel):
    """Master list of offered treatments / procedures."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, blank=True)
    default_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class TreatmentPlan(TimeStampedModel):
    STATUS = [
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="treatment_plans"
    )
    doctor = models.ForeignKey(
        Doctor, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="treatment_plans",
    )
    title = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS, default="DRAFT")
    progress_percent = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.patient.full_name})"

    def recompute_progress(self):
        treatments = Treatment.objects.filter(stage__plan=self)
        total = treatments.count()
        if not total:
            self.progress_percent = 0
        else:
            done = treatments.filter(status="COMPLETED").count()
            self.progress_percent = round(done * 100 / total)
        if self.progress_percent == 100 and self.status == "ACTIVE":
            self.status = "COMPLETED"
        self.save(update_fields=["progress_percent", "status"])


class TreatmentStage(TimeStampedModel):
    STATUS = [("PENDING", "Pending"), ("IN_PROGRESS", "In Progress"),
              ("COMPLETED", "Completed")]

    plan = models.ForeignKey(
        TreatmentPlan, on_delete=models.CASCADE, related_name="stages"
    )
    order = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=120)
    status = models.CharField(max_length=12, choices=STATUS, default="PENDING")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.name}"


class Treatment(TimeStampedModel):
    STATUS = [("PLANNED", "Planned"), ("IN_PROGRESS", "In Progress"),
              ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")]

    stage = models.ForeignKey(
        TreatmentStage, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="treatments",
    )
    catalog_item = models.ForeignKey(
        TreatmentCatalog, null=True, blank=True, on_delete=models.SET_NULL
    )
    visit = models.ForeignKey(
        "visits.Visit", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="treatments",
    )
    tooth = models.ForeignKey(
        "dental_charts.Tooth", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="treatments",
    )
    description = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="PLANNED")
    clinical_notes = models.TextField(blank=True)
    performed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        label = self.description or (self.catalog_item.name if self.catalog_item else "Treatment")
        return f"{label} ({self.status})"

    @property
    def total(self):
        return (self.unit_price or Decimal("0")) * self.quantity

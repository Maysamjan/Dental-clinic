from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.patients.models import Patient

ZERO = Decimal("0.00")


class Invoice(TimeStampedModel):
    STATUS = [("UNPAID", "Unpaid"), ("PARTIAL", "Partial"), ("PAID", "Paid")]

    number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="invoices"
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    issue_date = models.DateField(default=timezone.localdate)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    status = models.CharField(max_length=8, choices=STATUS, default="UNPAID")
    notes = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        indexes = [models.Index(fields=["status"]), models.Index(fields=["issue_date"])]

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            last = Invoice.objects.order_by("-id").first()
            nxt = (last.id + 1) if last else 1
            self.number = f"INV-{nxt:06d}"
        super().save(*args, **kwargs)

    def recompute(self):
        self.subtotal = sum((i.line_total for i in self.items.all()), ZERO)
        self.total = self.subtotal - self.discount + self.tax
        self.paid_amount = sum((p.amount for p in self.payments.all()), ZERO)
        self.balance = self.total - self.paid_amount
        if self.paid_amount <= ZERO:
            self.status = "UNPAID"
        elif self.balance <= ZERO:
            self.status = "PAID"
        else:
            self.status = "PARTIAL"
        self.save(update_fields=[
            "subtotal", "total", "paid_amount", "balance", "status", "updated_at"
        ])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    treatment = models.ForeignKey(
        "treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)

    def save(self, *args, **kwargs):
        self.line_total = (self.unit_price or ZERO) * self.quantity
        super().save(*args, **kwargs)


class InstallmentPlan(TimeStampedModel):
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name="installment_plan"
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    number_of_installments = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"Plan for {self.invoice.number}"


class Installment(models.Model):
    STATUS = [("PENDING", "Pending"), ("PARTIAL", "Partial"), ("PAID", "Paid")]

    plan = models.ForeignKey(
        InstallmentPlan, on_delete=models.CASCADE, related_name="installments"
    )
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    status = models.CharField(max_length=8, choices=STATUS, default="PENDING")

    class Meta:
        ordering = ["due_date"]


class Payment(TimeStampedModel):
    METHOD = [("CASH", "Cash"), ("BANK_TRANSFER", "Bank Transfer")]

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    installment = models.ForeignKey(
        Installment, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=14, choices=METHOD, default="CASH")
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reference = models.CharField(max_length=80, blank=True)
    paid_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.amount} for {self.invoice.number}"

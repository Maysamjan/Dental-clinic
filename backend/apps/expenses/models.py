from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class ExpenseCategory(models.Model):
    DEFAULTS = ["Salaries", "Utilities", "Supplies", "Rent", "Maintenance", "Other"]

    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Expense categories"

    def __str__(self):
        return self.name


class Expense(TimeStampedModel):
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT, related_name="expenses"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.localdate)
    description = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta(TimeStampedModel.Meta):
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return f"{self.category} - {self.amount}"

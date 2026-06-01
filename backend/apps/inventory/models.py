from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryItem(TimeStampedModel):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, blank=True)
    unit = models.CharField(max_length=30, default="pcs")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.ForeignKey(
        Supplier, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="items",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock


class InventoryTransaction(TimeStampedModel):
    TYPES = [("IN", "Stock In"), ("OUT", "Stock Out")]

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="transactions"
    )
    type = models.CharField(max_length=3, choices=TYPES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reason = models.CharField(max_length=200, blank=True)
    supplier = models.ForeignKey(
        Supplier, null=True, blank=True, on_delete=models.SET_NULL
    )
    treatment = models.ForeignKey(
        "treatments.Treatment", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="inventory_transactions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.type} {self.quantity} {self.item.name}"

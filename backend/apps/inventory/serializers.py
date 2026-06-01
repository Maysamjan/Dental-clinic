from rest_framework import serializers

from apps.core.validators import positive
from .models import Supplier, InventoryItem, InventoryTransaction


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "phone", "address"]


class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id", "name", "category", "unit", "quantity", "minimum_stock",
            "unit_cost", "supplier", "supplier_name", "is_low_stock",
        ]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = [
            "id", "item", "item_name", "type", "quantity", "unit_cost",
            "reason", "supplier", "treatment", "created_by", "created_at",
        ]
        read_only_fields = ["created_by"]

    def validate_quantity(self, value):
        return positive(value, "Quantity")

    def validate(self, attrs):
        # Prevent stocking out more than is available.
        if attrs.get("type") == "OUT":
            item = attrs.get("item")
            qty = attrs.get("quantity")
            if item and qty and qty > item.quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Only {item.quantity} {item.unit} of {item.name} in stock."}
                )
        return attrs

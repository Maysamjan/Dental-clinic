from rest_framework import serializers

from apps.core.validators import positive
from .models import Expense, ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ["id", "name"]


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "category", "category_name", "amount",
            "date", "description", "recorded_by", "created_at",
        ]
        read_only_fields = ["recorded_by"]

    def validate_amount(self, value):
        return positive(value, "Amount")

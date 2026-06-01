"""Reusable field validators shared across serializers."""
from datetime import date
from decimal import Decimal

from rest_framework import serializers


def non_negative(value, field="value"):
    if value is not None and value < 0:
        raise serializers.ValidationError(f"{field} cannot be negative.")
    return value


def positive(value, field="value"):
    if value is None or value <= 0:
        raise serializers.ValidationError(f"{field} must be greater than zero.")
    return value


def not_future_date(value, field="date"):
    if value and value > date.today():
        raise serializers.ValidationError(f"{field} cannot be in the future.")
    return value


def positive_quantity(value):
    if value is None or value < 1:
        raise serializers.ValidationError("Quantity must be at least 1.")
    return value


ZERO = Decimal("0")

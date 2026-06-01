"""Reusable field validators shared across serializers."""
import os
from datetime import date
from decimal import Decimal

from django.conf import settings
from rest_framework import serializers


def validate_upload(file, allowed_extensions=None, max_mb=None):
    """Validate an uploaded file's extension and size."""
    if file is None:
        return file
    allowed = allowed_extensions or settings.ALLOWED_DOCUMENT_EXTENSIONS
    max_mb = max_mb or settings.MAX_UPLOAD_SIZE_MB

    ext = os.path.splitext(file.name)[1].lower().lstrip(".")
    if ext not in allowed:
        raise serializers.ValidationError(
            f"Unsupported file type '.{ext}'. Allowed: {', '.join(allowed)}."
        )
    size = getattr(file, "size", 0) or 0
    if size > max_mb * 1024 * 1024:
        raise serializers.ValidationError(f"File exceeds the {max_mb}MB limit.")
    return file


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

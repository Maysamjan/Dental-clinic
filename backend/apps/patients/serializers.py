from rest_framework import serializers

from django.conf import settings

from apps.core.validators import not_future_date, validate_upload
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "code", "full_name", "gender", "date_of_birth", "age",
            "phone", "address", "registration_date",
            "emergency_contact_name", "emergency_contact_phone",
            "medical_history", "allergies", "notes", "photo",
            "is_archived", "created_at", "updated_at",
        ]
        read_only_fields = ["code", "created_at", "updated_at"]

    def validate_date_of_birth(self, value):
        return not_future_date(value, "Date of birth")

    def validate_full_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Full name is required.")
        return value.strip()

    def validate_photo(self, value):
        return validate_upload(value, settings.ALLOWED_IMAGE_EXTENSIONS, max_mb=10)


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists / dropdowns."""

    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "code", "full_name", "gender", "age", "phone", "is_archived"]

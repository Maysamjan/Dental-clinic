from rest_framework import serializers

from .models import ClinicInfo


class ClinicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicInfo
        fields = [
            "id", "name", "address", "phone", "email", "website", "logo",
            "default_language", "default_calendar", "currency",
            "tax_enabled", "tax_percent", "invoice_footer",
            "prescription_header", "prescription_footer",
            "appointment_duration_minutes", "working_hours", "settings",
        ]

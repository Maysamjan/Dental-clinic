from rest_framework import serializers

from .models import ClinicInfo


class ClinicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicInfo
        fields = [
            "id", "name", "address", "phone", "email", "logo",
            "default_language", "default_calendar", "currency", "settings",
        ]

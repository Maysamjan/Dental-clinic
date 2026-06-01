from rest_framework import serializers

from .models import FollowUp


class FollowUpSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_phone = serializers.CharField(source="patient.phone", read_only=True)

    class Meta:
        model = FollowUp
        fields = [
            "id", "patient", "patient_name", "patient_phone", "type",
            "due_date", "note", "status", "created_by", "created_at",
        ]
        read_only_fields = ["created_by"]

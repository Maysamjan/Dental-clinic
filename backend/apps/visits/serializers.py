from rest_framework import serializers

from .models import Visit


class VisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_code = serializers.CharField(source="patient.code", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)

    class Meta:
        model = Visit
        fields = [
            "id", "patient", "patient_name", "patient_code",
            "doctor", "doctor_name", "appointment",
            "visit_date", "visit_time",
            "chief_complaint", "clinical_findings", "diagnosis", "notes",
            "queue_number", "arrival_time", "workflow_status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["queue_number", "arrival_time"]


class QueueItemSerializer(serializers.ModelSerializer):
    """Compact payload for the live doctor queue."""

    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    medical_summary = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            "id", "queue_number", "patient", "patient_name",
            "arrival_time", "workflow_status", "doctor", "medical_summary",
        ]

    def get_medical_summary(self, obj):
        p = obj.patient
        parts = []
        if p.allergies:
            parts.append(f"Allergies: {p.allergies}")
        if p.medical_history:
            parts.append(p.medical_history[:160])
        return " | ".join(parts)

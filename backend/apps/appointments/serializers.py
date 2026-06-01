from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Appointment


def clinic_appointment_duration():
    """Default appointment length (minutes), configurable in clinic settings."""
    try:
        from apps.dashboard.models import ClinicInfo

        return int(ClinicInfo.load().settings.get("appointment_duration_minutes", 30))
    except Exception:
        return 30


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_code = serializers.CharField(source="patient.code", read_only=True)
    patient_phone = serializers.CharField(source="patient.phone", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    has_visit = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "patient", "patient_name", "patient_code", "patient_phone",
            "doctor", "doctor_name", "start", "end",
            "reason", "status", "notes", "has_visit", "created_at",
        ]

    def get_has_visit(self, obj):
        return hasattr(obj, "visit")

    def validate(self, attrs):
        start = attrs.get("start", getattr(self.instance, "start", None))
        end = attrs.get("end", getattr(self.instance, "end", None))

        # Auto-fill end from the configured default duration.
        if start and not end:
            end = start + timedelta(minutes=clinic_appointment_duration())
            attrs["end"] = end

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end": "End time must be after the start time."}
            )

        # Reject scheduling brand-new appointments in the past.
        if start and self.instance is None and start < timezone.now() - timedelta(minutes=1):
            raise serializers.ValidationError(
                {"start": "Cannot schedule an appointment in the past."}
            )

        # Prevent double-booking the same doctor for an overlapping slot.
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        if doctor and start and end:
            clash = Appointment.objects.filter(
                doctor=doctor, start__lt=end, end__gt=start,
            ).exclude(status__in=["CANCELLED", "NO_SHOW"])
            if self.instance:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise serializers.ValidationError(
                    {"start": "This doctor already has an appointment in that slot."}
                )
        return attrs

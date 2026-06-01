from rest_framework import serializers

from .models import DentalChart, Tooth, ToothCondition


class ToothConditionSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(
        source="recorded_by.full_name", read_only=True
    )

    class Meta:
        model = ToothCondition
        fields = [
            "id", "tooth", "condition", "surface", "note",
            "recorded_by", "recorded_by_name", "treatment", "created_at",
        ]
        read_only_fields = ["recorded_by"]


class ToothSerializer(serializers.ModelSerializer):
    conditions = ToothConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Tooth
        fields = ["id", "fdi_number", "name", "status", "conditions"]


class DentalChartSerializer(serializers.ModelSerializer):
    teeth = ToothSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)

    class Meta:
        model = DentalChart
        fields = ["id", "patient", "patient_name", "dentition", "teeth", "updated_at"]

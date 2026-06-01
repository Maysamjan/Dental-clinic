from rest_framework import serializers

from .models import TreatmentCatalog, TreatmentPlan, TreatmentStage, Treatment


class TreatmentCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentCatalog
        fields = ["id", "code", "name", "category", "default_price", "is_active"]


class TreatmentSerializer(serializers.ModelSerializer):
    catalog_name = serializers.CharField(source="catalog_item.name", read_only=True)
    tooth_number = serializers.IntegerField(source="tooth.fdi_number", read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Treatment
        fields = [
            "id", "stage", "catalog_item", "catalog_name", "visit", "tooth",
            "tooth_number", "description", "quantity", "unit_price", "total",
            "status", "clinical_notes", "performed_at", "created_at",
        ]


class TreatmentStageSerializer(serializers.ModelSerializer):
    treatments = TreatmentSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentStage
        fields = ["id", "plan", "order", "name", "status", "treatments"]


class TreatmentPlanSerializer(serializers.ModelSerializer):
    stages = TreatmentStageSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    actual_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    planned_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = [
            "id", "patient", "patient_name", "doctor", "doctor_name",
            "title", "status", "progress_percent", "estimated_cost",
            "actual_cost", "planned_cost", "stages", "created_at",
        ]
        read_only_fields = ["progress_percent"]

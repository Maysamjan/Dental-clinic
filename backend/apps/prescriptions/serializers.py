from rest_framework import serializers

from .models import Prescription, PrescriptionItem, PrescriptionTemplate


class PrescriptionTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionTemplate
        fields = ["id", "name", "description", "items"]


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ["id", "medication", "dosage", "frequency", "duration", "notes"]


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id", "patient", "patient_name", "doctor", "doctor_name",
            "visit", "notes", "items", "created_at",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        prescription = Prescription.objects.create(**validated_data)
        PrescriptionItem.objects.bulk_create(
            [PrescriptionItem(prescription=prescription, **item) for item in items]
        )
        return prescription

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if items is not None:
            instance.items.all().delete()
            PrescriptionItem.objects.bulk_create(
                [PrescriptionItem(prescription=instance, **item) for item in items]
            )
        return instance

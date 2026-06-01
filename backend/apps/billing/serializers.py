from rest_framework import serializers

from .models import (
    Invoice, InvoiceItem, Payment, InstallmentPlan, Installment,
)


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            "id", "treatment", "description", "quantity",
            "unit_price", "line_total",
        ]
        read_only_fields = ["line_total"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_code = serializers.CharField(source="patient.code", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "number", "patient", "patient_name", "patient_code",
            "issued_by", "issue_date", "subtotal", "discount", "tax",
            "total", "paid_amount", "balance", "status", "notes",
            "items", "created_at",
        ]
        read_only_fields = [
            "number", "subtotal", "total", "paid_amount", "balance", "status",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)
        for item in items:
            InvoiceItem.objects.create(invoice=invoice, **item)
        invoice.recompute()
        return invoice

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if items is not None:
            instance.items.all().delete()
            for item in items:
                InvoiceItem.objects.create(invoice=instance, **item)
        instance.recompute()
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.number", read_only=True)
    patient_name = serializers.CharField(
        source="invoice.patient.full_name", read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id", "invoice", "invoice_number", "patient_name", "installment",
            "amount", "method", "received_by", "reference", "paid_at",
        ]
        read_only_fields = ["received_by"]

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        amount = attrs.get("amount", getattr(self.instance, "amount", None))
        invoice = attrs.get("invoice", getattr(self.instance, "invoice", None))
        if invoice and amount:
            # Remaining balance, adding back this payment's old amount when editing.
            remaining = invoice.balance
            if self.instance is not None:
                remaining += self.instance.amount
            if amount > remaining:
                raise serializers.ValidationError(
                    {"amount": f"Payment exceeds the remaining balance ({remaining})."}
                )
        return attrs


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ["id", "plan", "due_date", "amount", "paid_amount", "status"]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = InstallmentPlan
        fields = [
            "id", "invoice", "total_amount",
            "number_of_installments", "installments",
        ]

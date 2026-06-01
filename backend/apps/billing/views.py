from datetime import timedelta
from decimal import Decimal

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from apps.core.pdf import build_pdf
from .models import Invoice, Payment, InstallmentPlan, Installment
from .serializers import (
    InvoiceSerializer, PaymentSerializer,
    InstallmentPlanSerializer, InstallmentSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    module = "billing"
    permission_classes = [HasModulePermission]
    queryset = Invoice.objects.select_related("patient").prefetch_related(
        "items", "payments"
    )
    serializer_class = InvoiceSerializer
    filterset_fields = ["status", "patient", "issue_date"]
    search_fields = ["number", "patient__full_name"]
    ordering_fields = ["issue_date", "total", "balance"]

    def perform_create(self, serializer):
        serializer.save(issued_by=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        inv = self.get_object()
        intro = [
            f"<b>Invoice:</b> {inv.number}",
            f"<b>Patient:</b> {inv.patient.full_name} ({inv.patient.code})",
            f"<b>Date:</b> {inv.issue_date}",
            f"<b>Status:</b> {inv.get_status_display()}",
        ]
        rows = [
            [i.description, str(i.quantity), f"{i.unit_price}", f"{i.line_total}"]
            for i in inv.items.all()
        ]
        footer = (
            f"Subtotal: {inv.subtotal} &nbsp;&nbsp; Discount: {inv.discount} &nbsp;&nbsp; "
            f"Tax: {inv.tax}<br/><b>Total: {inv.total}</b> &nbsp;&nbsp; "
            f"Paid: {inv.paid_amount} &nbsp;&nbsp; Balance: {inv.balance}"
        )
        pdf = build_pdf(
            "Invoice", intro,
            ["Description", "Qty", "Unit Price", "Total"], rows, footer,
        )
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="{inv.number}.pdf"'
        return resp


class PaymentViewSet(viewsets.ModelViewSet):
    module = "payments"
    permission_classes = [HasModulePermission]
    queryset = Payment.objects.select_related("invoice", "invoice__patient")
    serializer_class = PaymentSerializer
    filterset_fields = ["invoice", "method", "installment"]
    ordering_fields = ["paid_at", "amount"]

    def perform_create(self, serializer):
        serializer.save(
            received_by=self.request.user if self.request.user.is_authenticated else None
        )


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    module = "installments"
    permission_classes = [HasModulePermission]
    queryset = InstallmentPlan.objects.select_related("invoice").prefetch_related(
        "installments"
    )
    serializer_class = InstallmentPlanSerializer
    filterset_fields = ["invoice"]

    def create(self, request, *args, **kwargs):
        """Create a plan and auto-generate evenly-split monthly installments."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        count = max(plan.number_of_installments, 1)
        each = (plan.total_amount / count).quantize(Decimal("0.01"))
        start = timezone.localdate()
        for i in range(count):
            amount = each if i < count - 1 else plan.total_amount - each * (count - 1)
            Installment.objects.create(
                plan=plan, due_date=start + timedelta(days=30 * (i + 1)), amount=amount
            )
        return Response(
            self.get_serializer(plan).data, status=status.HTTP_201_CREATED
        )


class InstallmentViewSet(viewsets.ModelViewSet):
    module = "installments"
    permission_classes = [HasModulePermission]
    queryset = Installment.objects.select_related("plan", "plan__invoice")
    serializer_class = InstallmentSerializer
    filterset_fields = ["plan", "status", "due_date"]

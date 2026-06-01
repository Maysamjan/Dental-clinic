from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, F, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from apps.core.permissions import HasModulePermission, user_has_perm
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.visits.models import Visit
from apps.billing.models import Invoice, Payment
from apps.inventory.models import InventoryItem
from apps.followups.models import FollowUp
from apps.audit.models import ActivityLog
from .models import ClinicInfo
from .serializers import ClinicInfoSerializer

ZERO = Decimal("0.00")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Aggregated KPIs for the main dashboard."""
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    todays_revenue = Payment.objects.filter(paid_at__date=today).aggregate(
        s=Sum("amount")
    )["s"] or ZERO

    outstanding = Invoice.objects.exclude(status="PAID").aggregate(
        count=Sum(F("balance") * 0 + 1), total=Sum("balance")
    )

    data = {
        "total_patients": Patient.objects.filter(is_archived=False).count(),
        "todays_patients": Visit.objects.filter(visit_date=today).values(
            "patient"
        ).distinct().count(),
        "todays_appointments": Appointment.objects.filter(start__date=today).count(),
        "todays_revenue": todays_revenue,
        "outstanding_invoices": Invoice.objects.exclude(status="PAID").count(),
        "outstanding_balance": outstanding["total"] or ZERO,
        "upcoming_followups": FollowUp.objects.filter(
            status="PENDING", due_date__range=[today, tomorrow]
        ).count(),
        "inventory_alerts": InventoryItem.objects.filter(
            quantity__lte=F("minimum_stock")
        ).count(),
        "queue_size": Visit.objects.filter(visit_date=today)
        .exclude(workflow_status="COMPLETED").count(),
        "recent_activities": list(
            ActivityLog.objects.values(
                "action", "entity", "summary", "created_at"
            )[:10]
        ),
    }
    return Response(data)


class ClinicInfoViewSet(viewsets.ViewSet):
    """Clinic information & system settings (Administration)."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(ClinicInfoSerializer(ClinicInfo.load()).data)

    def update(self, request, pk=None):
        if not user_has_perm(request.user, "settings.change"):
            return Response(status=403)
        obj = ClinicInfo.load()
        serializer = ClinicInfoSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Support PATCH /settings/1/
    partial_update = update

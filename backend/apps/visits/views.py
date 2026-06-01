from datetime import date

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from .models import Visit
from .serializers import VisitSerializer, QueueItemSerializer

# Allowed workflow transitions.
TRANSITIONS = {
    "WAITING": {"IN_CONSULTATION"},
    "IN_CONSULTATION": {"TREATMENT_IN_PROGRESS", "COMPLETED"},
    "TREATMENT_IN_PROGRESS": {"COMPLETED"},
    "COMPLETED": set(),
}


class VisitViewSet(viewsets.ModelViewSet):
    module = "visits"
    permission_classes = [HasModulePermission]
    queryset = Visit.objects.select_related("patient", "doctor", "doctor__user")
    serializer_class = VisitSerializer
    filterset_fields = ["doctor", "patient", "workflow_status", "visit_date"]
    search_fields = ["patient__full_name", "chief_complaint", "diagnosis"]

    def perform_create(self, serializer):
        # New arrivals enter the queue.
        visit = serializer.save()
        if visit.workflow_status == "WAITING" and visit.queue_number is None:
            visit.queue_number = Visit.next_queue_number(visit.visit_date)
            visit.arrival_time = timezone.now()
            visit.save(update_fields=["queue_number", "arrival_time"])

    @action(detail=False, methods=["get"], url_path="queue")
    def queue(self, request):
        """Today's live queue (Waiting / In Consultation / Treatment)."""
        today = date.today()
        qs = (
            self.get_queryset()
            .filter(visit_date=today)
            .exclude(workflow_status="COMPLETED")
            .order_by("queue_number")
        )
        doctor_id = request.query_params.get("doctor")
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        return Response(QueueItemSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="advance")
    def advance(self, request, pk=None):
        """Move a visit to the next workflow status (validated)."""
        visit = self.get_object()
        target = request.data.get("status")
        if target not in TRANSITIONS.get(visit.workflow_status, set()):
            return Response(
                {"detail": f"Invalid transition {visit.workflow_status} -> {target}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        visit.workflow_status = target
        visit.save(update_fields=["workflow_status", "updated_at"])
        return Response(VisitSerializer(visit).data)

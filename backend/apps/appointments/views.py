from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from apps.audit.utils import log_activity
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    module = "appointments"
    permission_classes = [HasModulePermission]
    queryset = Appointment.objects.select_related("patient", "doctor", "doctor__user")
    serializer_class = AppointmentSerializer
    filterset_fields = ["status", "doctor", "patient"]
    search_fields = ["patient__full_name", "reason"]
    ordering_fields = ["start", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        # Calendar range filtering: ?from=YYYY-MM-DD&to=YYYY-MM-DD
        start_from = params.get("from")
        start_to = params.get("to")
        if start_from:
            qs = qs.filter(start__date__gte=parse_date(start_from))
        if start_to:
            qs = qs.filter(start__date__lte=parse_date(start_to))
        return qs

    def perform_create(self, serializer):
        appt = serializer.save()
        log_activity(
            action="CREATE", entity="Appointment", entity_id=appt.id,
            summary=f"Appointment for {appt.patient.full_name} @ {appt.start:%Y-%m-%d %H:%M}",
        )

    def _set_status(self, appt, new_status, summary):
        appt.status = new_status
        appt.save(update_fields=["status", "updated_at"])
        log_activity(action="UPDATE", entity="Appointment", entity_id=appt.id, summary=summary)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appt = self.get_object()
        self._set_status(appt, "CONFIRMED", f"Confirmed appointment #{appt.id}")
        return Response(AppointmentSerializer(appt).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appt = self.get_object()
        self._set_status(appt, "CANCELLED", f"Cancelled appointment #{appt.id}")
        return Response(AppointmentSerializer(appt).data)

    @action(detail=True, methods=["post"], url_path="no-show")
    def no_show(self, request, pk=None):
        appt = self.get_object()
        self._set_status(appt, "NO_SHOW", f"No-show appointment #{appt.id}")
        return Response(AppointmentSerializer(appt).data)

    @action(detail=True, methods=["post"])
    def arrive(self, request, pk=None):
        """Mark the patient as arrived and place them in the live queue.

        Creates (or reuses) the Visit linked to this appointment with status
        WAITING and a queue number for today.
        """
        from apps.visits.models import Visit
        from apps.visits.serializers import VisitSerializer

        appt = self.get_object()
        if appt.status in ("CANCELLED", "NO_SHOW", "COMPLETED"):
            return Response(
                {"detail": f"Cannot arrive a {appt.get_status_display()} appointment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        visit = Visit.objects.filter(appointment=appt).first()
        if not visit:
            visit = Visit.objects.create(
                patient=appt.patient,
                doctor=appt.doctor,
                appointment=appt,
                workflow_status="WAITING",
                queue_number=Visit.next_queue_number(),
                arrival_time=timezone.now(),
                chief_complaint=appt.reason or "",
            )
        appt.status = "ARRIVED"
        appt.save(update_fields=["status", "updated_at"])
        log_activity(
            action="UPDATE", entity="Appointment", entity_id=appt.id,
            summary=f"Patient arrived: {appt.patient.full_name} (queue #{visit.queue_number})",
        )
        return Response(
            {"appointment": AppointmentSerializer(appt).data,
             "visit": VisitSerializer(visit).data},
            status=status.HTTP_201_CREATED,
        )

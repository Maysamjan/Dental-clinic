from django.utils.dateparse import parse_date
from rest_framework import viewsets

from apps.core.permissions import HasModulePermission
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

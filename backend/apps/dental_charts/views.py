from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from apps.patients.models import Patient
from .models import DentalChart, Tooth, ToothCondition
from .serializers import (
    DentalChartSerializer, ToothSerializer, ToothConditionSerializer,
)
from .services import get_or_create_chart


class DentalChartViewSet(viewsets.ReadOnlyModelViewSet):
    module = "dental_charts"
    permission_classes = [HasModulePermission]
    queryset = DentalChart.objects.prefetch_related("teeth__conditions")
    serializer_class = DentalChartSerializer

    @action(detail=False, methods=["get"], url_path="by-patient/(?P<patient_id>[^/.]+)")
    def by_patient(self, request, patient_id=None):
        """Fetch (or lazily create) the chart for a given patient."""
        patient = Patient.objects.get(pk=patient_id)
        dentition = request.query_params.get("dentition", "ADULT")
        chart = get_or_create_chart(patient, dentition)
        return Response(DentalChartSerializer(chart).data)


class ToothViewSet(viewsets.ModelViewSet):
    module = "dental_charts"
    permission_classes = [HasModulePermission]
    queryset = Tooth.objects.select_related("chart")
    serializer_class = ToothSerializer
    filterset_fields = ["chart", "status"]
    http_method_names = ["get", "patch", "head", "options"]

    def partial_update(self, request, *args, **kwargs):
        """Update a tooth's status and append a history entry."""
        tooth = self.get_object()
        new_status = request.data.get("status")
        response = super().partial_update(request, *args, **kwargs)
        if new_status:
            ToothCondition.objects.create(
                tooth=tooth,
                condition=new_status,
                surface=request.data.get("surface", ""),
                note=request.data.get("note", ""),
                recorded_by=request.user if request.user.is_authenticated else None,
            )
        return response


class ToothConditionViewSet(viewsets.ModelViewSet):
    module = "dental_charts"
    permission_classes = [HasModulePermission]
    queryset = ToothCondition.objects.select_related("tooth", "recorded_by")
    serializer_class = ToothConditionSerializer
    filterset_fields = ["tooth", "condition"]

    def perform_create(self, serializer):
        condition = serializer.save(
            recorded_by=self.request.user if self.request.user.is_authenticated else None
        )
        # Keep the tooth's current status in sync with its latest condition.
        Tooth.objects.filter(pk=condition.tooth_id).update(status=condition.condition)

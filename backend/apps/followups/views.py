from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from .models import FollowUp
from .serializers import FollowUpSerializer


class FollowUpViewSet(viewsets.ModelViewSet):
    module = "followups"
    permission_classes = [HasModulePermission]
    queryset = FollowUp.objects.select_related("patient")
    serializer_class = FollowUpSerializer
    filterset_fields = ["type", "status", "due_date", "patient"]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """Follow-up widget data: due today, due tomorrow, payment follow-ups."""
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        pending = self.get_queryset().filter(status="PENDING")
        data = {
            "due_today": FollowUpSerializer(
                pending.filter(due_date=today), many=True
            ).data,
            "due_tomorrow": FollowUpSerializer(
                pending.filter(due_date=tomorrow), many=True
            ).data,
            "payment_followups": FollowUpSerializer(
                pending.filter(type="PAYMENT"), many=True
            ).data,
        }
        return Response(data)

from rest_framework import mixins, viewsets, serializers

from apps.core.permissions import HasModulePermission
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id", "user", "username", "action", "entity",
            "entity_id", "summary", "ip_address", "created_at",
        ]


class ActivityLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    module = "audit"
    permission_classes = [HasModulePermission]
    queryset = ActivityLog.objects.select_related("user").all()
    serializer_class = ActivityLogSerializer
    filterset_fields = ["action", "entity", "user"]
    search_fields = ["summary", "entity", "entity_id"]

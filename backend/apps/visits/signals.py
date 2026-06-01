from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.realtime import broadcast, WORKFLOW_GROUP, DASHBOARD_GROUP
from apps.audit.utils import log_activity
from .models import Visit
from .serializers import QueueItemSerializer


@receiver(post_save, sender=Visit)
def on_visit_saved(sender, instance, created, **kwargs):
    # Broadcast queue change to reception & doctor dashboards.
    broadcast(
        WORKFLOW_GROUP,
        "visit.created" if created else "visit.updated",
        QueueItemSerializer(instance).data,
    )
    # Nudge the dashboard to refresh KPIs.
    broadcast(DASHBOARD_GROUP, "refresh", {"reason": "visit"})

    action = "CREATE" if created else "UPDATE"
    log_activity(
        action=action, entity="Visit", entity_id=instance.id,
        summary=f"Visit {instance.id} for {instance.patient.full_name} "
                f"({instance.workflow_status})",
    )

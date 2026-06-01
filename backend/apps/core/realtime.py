"""Helpers to broadcast events to Channels groups from synchronous code."""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

WORKFLOW_GROUP = "clinic_workflow"
DASHBOARD_GROUP = "clinic_dashboard"


def broadcast(group, event_type, payload):
    """Send ``payload`` to every consumer in ``group``.

    Real-time delivery is best-effort: a channel-layer/Redis outage must never
    break the primary database operation that triggered the broadcast.
    """
    try:
        layer = get_channel_layer()
        if layer is None:
            return
        async_to_sync(layer.group_send)(
            group, {"type": "broadcast", "event": event_type, "payload": payload}
        )
    except Exception:  # pragma: no cover - defensive
        logger.warning("Realtime broadcast to %s failed", group, exc_info=True)

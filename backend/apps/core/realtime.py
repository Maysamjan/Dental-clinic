"""Helpers to broadcast events to Channels groups from synchronous code."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

WORKFLOW_GROUP = "clinic_workflow"
DASHBOARD_GROUP = "clinic_dashboard"


def broadcast(group, event_type, payload):
    """Send ``payload`` to every consumer in ``group``."""
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        group, {"type": "broadcast", "event": event_type, "payload": payload}
    )

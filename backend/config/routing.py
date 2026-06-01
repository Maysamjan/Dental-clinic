"""WebSocket URL routing."""
from django.urls import path

from apps.visits.consumers import WorkflowConsumer
from apps.dashboard.consumers import DashboardConsumer

websocket_urlpatterns = [
    path("ws/workflow/", WorkflowConsumer.as_asgi()),
    path("ws/dashboard/", DashboardConsumer.as_asgi()),
]

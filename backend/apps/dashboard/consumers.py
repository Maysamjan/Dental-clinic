"""WebSocket consumer that pushes live dashboard refresh signals."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer

from apps.core.realtime import DASHBOARD_GROUP


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(DASHBOARD_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(DASHBOARD_GROUP, self.channel_name)

    async def broadcast(self, message):
        await self.send(
            json.dumps({"event": message["event"], "payload": message["payload"]})
        )

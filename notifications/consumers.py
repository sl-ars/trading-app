import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from notifications.models import Notification
from datetime import datetime


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Handles WebSocket connection """
        self.user = self.scope.get("user", AnonymousUser())

        if not self.user or self.user.is_anonymous:
            await self.close(code=403)
            return

        self.room_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send unread notifications on connect
        unread_notifications = await self.get_unread_notifications()
        for notification in unread_notifications:
            await self.send(text_data=json.dumps({"notification": notification}))

    async def disconnect(self, close_code):
        """ Handles WebSocket disconnection """
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_notification(self, event):
        """ Sends real-time notifications """

        notification_data = {
            "notification": {
                "message": "LOX"+event["message"],
                "created_at": event.get("created_at")
            }
        }
        await self.send(text_data=json.dumps(notification_data))

    @database_sync_to_async
    def get_unread_notifications(self):
        """ Retrieves unread notifications and formats them correctly """
        return [
            {
                "notification": {
                    "message": notif.message,
                    "created_at": notif.created_at.strftime("%Y-%m-%d %H:%M:%S")  # Fix datetime serialization
                }
            }
            for notif in Notification.objects.filter(user=self.user, read=False)
        ]

    async def notify(self, event):
        """ Handles `notify` event type and ensures correct format """


        notification_data = {
            "notification": {
                "message": "LOX"+event["message"],
                "created_at": event.get("created_at")
            }
        }
        await self.send(text_data=json.dumps(notification_data))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            # Reject the connection if the user is not authenticated
            await self.close()
            return
        
        self.room_name = f"user_{self.user.id}_notifications"
        self.room_group_name = f"notifications_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        
        if message == 'get_unread_count':
            count = await self.get_unread_notification_count()
            
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': count
            }))
    
    # Receive message from room group
    async def notification_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def get_unread_notification_count(self):
        from .models import Notification
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

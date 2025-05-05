from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ('id', 'sender', 'notification_type', 'text', 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'notification_type', 'text', 'created_at')

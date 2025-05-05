from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import Notification

def create_notification(recipient, sender, notification_type, content_object, text):
    """
    Create a notification without WebSocket functionality.
    """
    # Create notification in database
    content_type = ContentType.objects.get_for_model(content_object)
    
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        content_type=content_type,
        object_id=content_object.id,
        text=text
    )
    
    return notification
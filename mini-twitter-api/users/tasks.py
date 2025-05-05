from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_follow_notification(follower_id, following_id):
    try:
        follower = User.objects.get(id=follower_id)
        following = User.objects.get(id=following_id)
        
        # In a real application, you would send an email here
        print(f"Sending notification: {follower.username} is now following {following.username}")
        
        # Example email sending (commented out)
        # send_mail(
        #     f'{follower.username} is now following you!',
        #     f'Hi {following.username}, {follower.username} has started following you on Mini Twitter.',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [following.email],
        #     fail_silently=False,
        # )
        
        return True
    except User.DoesNotExist:
        return False
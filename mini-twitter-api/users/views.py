from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied
from .models import Profile, Follow
from .serializers import UserSerializer, UserRegistrationSerializer, ProfileSerializer, FollowSerializer
from .tasks import send_follow_notification

# Import create_notification only if notifications app is installed
try:
    from notifications.services import create_notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    # Create a dummy function if notifications are not enabled
    def create_notification(*args, **kwargs):
        pass

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()
        user = request.user
        
        if user == user_to_follow:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=user,
            following=user_to_follow
        )
        
        if created:
            # Update follower and following counts
            with transaction.atomic():
                user.profile.following_count += 1
                user.profile.save()
                user_to_follow.profile.followers_count += 1
                user_to_follow.profile.save()
            
            # Invalidate cache
            cache.delete(f'feed_{user.id}')
            
            # Send notification
            send_follow_notification.delay(user.id, user_to_follow.id)
            
            # Create notification
            if NOTIFICATIONS_ENABLED:
                create_notification(
                    recipient=user_to_follow,
                    sender=user,
                    notification_type='follow',
                    content_object=follow,
                    text=f"{user.username} started following you."
                )
            
            return Response(
                {"detail": f"You are now following {user_to_follow.username}."},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"detail": f"You are already following {user_to_follow.username}."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        user = request.user
        
        try:
            follow = Follow.objects.get(
                follower=user,
                following=user_to_unfollow
            )
            follow.delete()
            
            # Update follower and following counts
            with transaction.atomic():
                user.profile.following_count -= 1
                user.profile.save()
                user_to_unfollow.profile.followers_count -= 1
                user_to_unfollow.profile.save()
            
            # Invalidate cache
            cache.delete(f'feed_{user.id}')
            
            return Response(
                {"detail": f"You have unfollowed {user_to_unfollow.username}."},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {"detail": f"You are not following {user_to_unfollow.username}."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        user = self.get_object()
        followers = User.objects.filter(following__following=user)
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        user = self.get_object()
        following = User.objects.filter(followers__follower=user)
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_my_profile(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.core.cache import cache
from django.db.models import Q, Count
from rest_framework.exceptions import PermissionDenied
from .models import Post, Like, Hashtag, PostHashtag, Retweet, Mention
from .serializers import PostSerializer, LikeSerializer, HashtagSerializer, RetweetSerializer
from users.models import Follow
from django.contrib.auth.models import User
from users.serializers import UserSerializer
from datetime import timedelta
from django.utils import timezone

# Import create_notification only if notifications app is installed
try:
    from notifications.services import create_notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    # Create a dummy function if notifications are not enabled
    def create_notification(*args, **kwargs):
        pass

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search', 'trending_hashtags']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by hashtag if specified
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            queryset = queryset.filter(hashtags__hashtag__name=hashtag)
        
        # Filter by mention if specified
        mention = self.request.query_params.get('mention')
        if mention:
            queryset = queryset.filter(mentions__user__username=mention)
        
        # Filter by type if specified
        post_type = self.request.query_params.get('type')
        if post_type == 'original':
            queryset = queryset.filter(is_retweet=False, is_reply=False)
        elif post_type == 'retweets':
            queryset = queryset.filter(is_retweet=True)
        elif post_type == 'replies':
            queryset = queryset.filter(is_reply=True)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) | 
                Q(user__username__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        # Check if this is a reply
        parent_id = self.request.data.get('parent')
        is_reply = parent_id is not None
        
        # Check if this is a retweet
        original_post_id = self.request.data.get('original_post')
        is_retweet = original_post_id is not None
        
        parent = None
        original_post = None
        
        if is_reply:
            try:
                parent = Post.objects.get(pk=parent_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError({"parent": "Parent post does not exist."})
        
        if is_retweet:
            try:
                original_post = Post.objects.get(pk=original_post_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError({"original_post": "Original post does not exist."})
        
        post = serializer.save(
            user=self.request.user,
            is_reply=is_reply,
            parent=parent,
            is_retweet=is_retweet,
            original_post=original_post
        )
        
        # Update reply count on parent post
        if is_reply and parent:
            with transaction.atomic():
                parent.replies_count += 1
                parent.save()
            
            # Create notification for reply
            if NOTIFICATIONS_ENABLED and parent.user != self.request.user:
                create_notification(
                    recipient=parent.user,
                    sender=self.request.user,
                    notification_type='reply',
                    content_object=post,
                    text=f"{self.request.user.username} replied to your post."
                )
        
        # Create retweet record and update retweet count
        if is_retweet and original_post:
            Retweet.objects.create(user=self.request.user, post=original_post)
            
            with transaction.atomic():
                original_post.retweets_count += 1
                original_post.save()
            
            # Create notification for retweet
            if NOTIFICATIONS_ENABLED and original_post.user != self.request.user:
                create_notification(
                    recipient=original_post.user,
                    sender=self.request.user,
                    notification_type='retweet',
                    content_object=post,
                    text=f"{self.request.user.username} retweeted your post."
                )
        
        # Create notifications for mentions
        if NOTIFICATIONS_ENABLED:
            for mention in post.mentions.all():
                if mention.user != self.request.user:
                    create_notification(
                        recipient=mention.user,
                        sender=self.request.user,
                        notification_type='mention',
                        content_object=post,
                        text=f"{self.request.user.username} mentioned you in a post."
                    )
    
    def perform_update(self, serializer):
        post = self.get_object()
        
        # Only allow the owner to update the post
        if post.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this post.")
        
        # Don't allow editing retweets
        if post.is_retweet:
            raise PermissionDenied("You cannot edit a retweet.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow the owner to delete the post
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        
        # If this is a reply, update the parent's reply count
        if instance.is_reply and instance.parent:
            with transaction.atomic():
                instance.parent.replies_count -= 1
                instance.parent.save()
        
        # If this is a retweet, update the original post's retweet count
        if instance.is_retweet and instance.original_post:
            with transaction.atomic():
                instance.original_post.retweets_count -= 1
                instance.original_post.save()
        
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(
            user=user,
            post=post
        )
        
        if created:
            # Update likes count
            with transaction.atomic():
                post.likes_count += 1
                post.save()
            
            # Invalidate cache
            cache.delete(f'feed_{user.id}')
            
            # Create notification (only if the post is not by the current user)
            if NOTIFICATIONS_ENABLED and post.user != user:
                create_notification(
                    recipient=post.user,
                    sender=user,
                    notification_type='like',
                    content_object=like,
                    text=f"{user.username} liked your post."
                )
            
            return Response(
                {"detail": "Post liked successfully."},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"detail": "You have already liked this post."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        try:
            like = Like.objects.get(
                user=user,
                post=post
            )
            like.delete()
            
            # Update likes count
            with transaction.atomic():
                post.likes_count -= 1
                post.save()
            
            # Invalidate cache
            cache.delete(f'feed_{user.id}')
            
            return Response(
                {"detail": "Post unliked successfully."},
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            return Response(
                {"detail": "You have not liked this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def retweet(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # Check if user has already retweeted this post
        if Retweet.objects.filter(user=user, post=post).exists():
            return Response(
                {"detail": "You have already retweeted this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new post that is a retweet
        retweet_post = Post.objects.create(
            user=user,
            content="",  # Retweets don't have their own content
            is_retweet=True,
            original_post=post
        )
        
        # Create the retweet record
        Retweet.objects.create(user=user, post=post)
        
        # Update retweet count
        with transaction.atomic():
            post.retweets_count += 1
            post.save()
        
        # Invalidate cache
        cache.delete(f'feed_{user.id}')
        
        # Create notification
        if NOTIFICATIONS_ENABLED and post.user != user:
            create_notification(
                recipient=post.user,
                sender=user,
                notification_type='retweet',
                content_object=retweet_post,
                text=f"{user.username} retweeted your post."
            )
        
        return Response(
            {"detail": "Post retweeted successfully."},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def unretweet(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        try:
            # Find the retweet record
            retweet = Retweet.objects.get(user=user, post=post)
            
            # Find the retweet post
            retweet_post = Post.objects.filter(
                user=user,
                is_retweet=True,
                original_post=post
            ).first()
            
            if retweet_post:
                retweet_post.delete()
            
            retweet.delete()
            
            # Update retweet count
            with transaction.atomic():
                post.retweets_count -= 1
                post.save()
            
            # Invalidate cache
            cache.delete(f'feed_{user.id}')
            
            return Response(
                {"detail": "Post unretweeted successfully."},
                status=status.HTTP_200_OK
            )
        except Retweet.DoesNotExist:
            return Response(
                {"detail": "You have not retweeted this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        post = self.get_object()
        likes = Like.objects.filter(post=post)
        users = User.objects.filter(likes__post=post)
        
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def retweets(self, request, pk=None):
        post = self.get_object()
        retweets = Retweet.objects.filter(post=post)
        users = User.objects.filter(retweets__post=post)
        
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        post = self.get_object()
        replies = Post.objects.filter(parent=post, is_reply=True)
        
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        user = request.user
        
        # Try to get feed from cache
        cached_feed = cache.get(f'feed_{user.id}')
        if cached_feed:
            return Response(cached_feed)
        
        # Get IDs of users that the current user follows
        following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
        
        # Include the user's own posts in the feed
        following_ids = list(following_ids) + [user.id]
        
        # Get posts from followed users and the user's own posts
        posts = Post.objects.filter(
            Q(user_id__in=following_ids) |  # Posts from followed users
            Q(mentions__user=user)  # Posts where the user is mentioned
        ).distinct().order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True, context={'request': request})
        
        # Cache the feed for 5 minutes
        cache.set(f'feed_{user.id}', serializer.data, 300)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.query_params.get('q', '')
        if not search_query:
            return Response(
                {"detail": "Search query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if it's a hashtag search
        if search_query.startswith('#'):
            hashtag = search_query[1:]  # Remove the # symbol
            posts = Post.objects.filter(hashtags__hashtag__name__iexact=hashtag)
            posts_serializer = self.get_serializer(posts, many=True, context={'request': request})
        
            return Response({
                'posts': posts_serializer.data,
                'users': [],
                'hashtag': hashtag
            })
    
        # Regular search
        # Search in posts content
        posts = Post.objects.filter(content__icontains=search_query)
        posts_serializer = self.get_serializer(posts, many=True, context={'request': request})
    
        # Search in usernames (limited to 5 results)
        users = User.objects.filter(username__icontains=search_query)[:5]
        users_serializer = UserSerializer(users, many=True)
    
        # Search in hashtags (limited to 5 results)
        hashtags = Hashtag.objects.filter(name__icontains=search_query)[:5]
        hashtags_serializer = HashtagSerializer(hashtags, many=True)
    
        return Response({
            'posts': posts_serializer.data,
            'users': users_serializer.data,
            'hashtags': hashtags_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def trending_hashtags(self, request):
        # Get hashtags used in the last 7 days
        last_week = timezone.now() - timedelta(days=7)
        
        # Get trending hashtags based on post count
        trending_hashtags = Hashtag.objects.filter(
            posts__post__created_at__gte=last_week
        ).annotate(
            recent_count=Count('posts')
        ).order_by('-recent_count')[:10]
        
        serializer = HashtagSerializer(trending_hashtags, many=True)
        return Response(serializer.data)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RetweetViewSet(viewsets.ModelViewSet):
    queryset = Retweet.objects.all()
    serializer_class = RetweetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Retweet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
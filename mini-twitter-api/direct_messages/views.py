from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth.models import User

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    
    def create(self, request):
        # Get or create a conversation between the current user and the specified user
        other_user_id = request.data.get('user_id')
        if not other_user_id:
            return Response(
                {"detail": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if a conversation already exists
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        )
        
        if conversations.exists():
            serializer = self.get_serializer(conversations.first())
            return Response(serializer.data)
        
        # Create a new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Mark messages as read
        unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
        unread_messages.update(is_read=True)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {"detail": "Message content is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save()  # This will update the updated_at field
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        user = request.user
        total_unread = Message.objects.filter(
            conversation__participants=user,
            is_read=False
        ).exclude(
            sender=user
        ).count()
        
        return Response({"unread_count": total_unread})

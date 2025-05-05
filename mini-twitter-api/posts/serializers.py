from rest_framework import serializers
from .models import Post, Like, Hashtag, PostHashtag, Retweet, Mention
from users.serializers import UserSerializer

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'name', 'post_count')

class MentionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Mention
        fields = ('id', 'user')

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_retweeted = serializers.SerializerMethodField()
    hashtags = serializers.SerializerMethodField()
    mentions = serializers.SerializerMethodField()
    original_post_data = serializers.SerializerMethodField()
    parent_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'user', 'content', 'image', 'likes_count', 'retweets_count', 
            'replies_count', 'is_liked', 'is_retweeted', 'hashtags', 'mentions',
            'is_retweet', 'original_post', 'original_post_data',
            'is_reply', 'parent', 'parent_data',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'likes_count', 'retweets_count', 'replies_count',
            'is_liked', 'is_retweeted', 'hashtags', 'mentions',
            'created_at', 'updated_at'
        )
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_is_retweeted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Retweet.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def get_hashtags(self, obj):
        hashtags = [ph.hashtag for ph in obj.hashtags.all()]
        return HashtagSerializer(hashtags, many=True).data
    
    def get_mentions(self, obj):
        mentions = obj.mentions.all()
        return MentionSerializer(mentions, many=True).data
    
    def get_original_post_data(self, obj):
        if obj.is_retweet and obj.original_post:
            return PostSerializer(obj.original_post, context=self.context).data
        return None
    
    def get_parent_data(self, obj):
        if obj.is_reply and obj.parent:
            return PostSerializer(obj.parent, context=self.context).data
        return None

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class RetweetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Retweet
        fields = ('id', 'user', 'post', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
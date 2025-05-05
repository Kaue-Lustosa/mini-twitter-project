from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Follow

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture')
        read_only_fields = ('id',)
    
    def get_profile_picture(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url
        return None

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = (
            'id', 'username', 'email', 'full_name', 'bio', 'location', 'website', 
            'birth_date', 'avatar', 'header_image', 'followers_count', 
            'following_count', 'posts_count', 'is_verified', 'created_at'
        )
        read_only_fields = (
            'id', 'username', 'email', 'full_name', 'followers_count', 
            'following_count', 'posts_count', 'is_verified', 'created_at'
        )
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    
    class Meta:
        model = Follow
        fields = ('id', 'follower', 'follower_username', 'following', 'following_username', 'created_at')
        read_only_fields = ('id', 'follower', 'follower_username', 'following_username', 'created_at')
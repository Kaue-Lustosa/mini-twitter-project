#!/usr/bin/env python
import os
import django
import time
import subprocess

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_twitter.settings')
django.setup()

def initialize_database():
    print("Initializing database...")
    
    # Run migrations
    print("Running migrations...")
    subprocess.run(['python', 'manage.py', 'makemigrations', 'users', 'posts'], check=True)
    subprocess.run(['python', 'manage.py', 'migrate'], check=True)
    
    # Now we can import models after migrations have been applied
    from django.contrib.auth.models import User
    from users.models import Profile, Follow
    from posts.models import Post, Like
    
    # Check if we need to create a superuser
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
    
    # Check if we need to create some test data
    if User.objects.count() <= 1:  # Only the superuser exists
        print("Creating test data...")
        
        # Create test users
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        
        # Update profiles
        user1.profile.bio = "This is user1's bio"
        user1.profile.save()
        
        user2.profile.bio = "This is user2's bio"
        user2.profile.save()
        
        # Create follow relationship
        Follow.objects.create(follower=user1, following=user2)
        
        # Update follower/following counts
        user1.profile.following_count = 1
        user1.profile.save()
        
        user2.profile.followers_count = 1
        user2.profile.save()
        
        # Create some posts
        post1 = Post.objects.create(
            user=user1,
            content="This is my first post! #firstpost #minitwitter"
        )
        
        post2 = Post.objects.create(
            user=user2,
            content="Hello from user2! #hello #minitwitter"
        )
        
        # Create likes
        Like.objects.create(user=user2, post=post1)
        Like.objects.create(user=user1, post=post2)
        
        # Update like counts
        post1.likes_count = 1
        post1.save()
        
        post2.likes_count = 1
        post2.save()
        
        print("Test data created successfully!")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    # Wait for database to be ready
    time.sleep(5)
    initialize_database()
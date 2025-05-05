from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Post, Like
from users.models import Follow

class PostTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        self.client.force_authenticate(user=self.user)
        self.post_data = {
            'content': 'This is a test post'
        }
    
    def test_create_post(self):
        url = reverse('post-list')
        response = self.client.post(url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().content, 'This is a test post')
        self.assertEqual(Post.objects.get().user, self.user)
    
    def test_like_post(self):
        post = Post.objects.create(user=self.other_user, content='Post to like')
        url = reverse('post-like', args=[post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.user, post=post).exists())
        
        # Check that likes count was updated
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 1)
    
    def test_unlike_post(self):
        post = Post.objects.create(user=self.other_user, content='Post to unlike')
        Like.objects.create(user=self.user, post=post)
        post.likes_count = 1
        post.save()
        
        url = reverse('post-unlike', args=[post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, post=post).exists())
        
        # Check that likes count was updated
        post.refresh_from_db()
        self.assertEqual(post.likes_count, 0)
    
    def test_feed(self):
        # Create a post from other_user
        Post.objects.create(user=self.other_user, content='Post from other user')
        
        # User is not following other_user yet, so feed should be empty
        url = reverse('post-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Follow other_user
        Follow.objects.create(follower=self.user, following=self.other_user)
        
        # Now feed should contain the post
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Post from other user')

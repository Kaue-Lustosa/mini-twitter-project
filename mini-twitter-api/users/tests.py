from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Profile, Follow

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpassword123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_register_user(self):
        self.client.force_authenticate(user=None)
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='testuser').email, 'test@example.com')
    
    def test_profile_created_on_user_creation(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
    
    def test_follow_user(self):
        new_user = User.objects.create_user(
            username='usertofollow',
            email='follow@example.com',
            password='followpassword123'
        )
        url = reverse('user-follow', args=[new_user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(follower=self.user, following=new_user).exists())
        
        # Check that counts were updated
        self.user.refresh_from_db()
        new_user.refresh_from_db()
        self.assertEqual(self.user.profile.following_count, 1)
        self.assertEqual(new_user.profile.followers_count, 1)
    
    def test_unfollow_user(self):
        new_user = User.objects.create_user(
            username='usertofollow',
            email='follow@example.com',
            password='followpassword123'
        )
        Follow.objects.create(follower=self.user, following=new_user)
        self.user.profile.following_count = 1
        self.user.profile.save()
        new_user.profile.followers_count = 1
        new_user.profile.save()
        
        url = reverse('user-unfollow', args=[new_user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Follow.objects.filter(follower=self.user, following=new_user).exists())
        
        # Check that counts were updated
        self.user.refresh_from_db()
        new_user.refresh_from_db()
        self.assertEqual(self.user.profile.following_count, 0)
        self.assertEqual(new_user.profile.followers_count, 0)

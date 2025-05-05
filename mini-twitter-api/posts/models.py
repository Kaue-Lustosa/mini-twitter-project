from django.db import models
from django.contrib.auth.models import User
import re

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    retweets_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    
    # For retweets
    original_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='retweets')
    is_retweet = models.BooleanField(default=False)
    
    # For replies
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_reply = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s post: {self.content[:50]}"

    def extract_and_save_hashtags(self):
        # Extract hashtags using regex
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, self.content)
        
        # Clear existing hashtags
        self.hashtags.all().delete()
        
        # Create new hashtags
        for tag_name in hashtags:
            tag, created = Hashtag.objects.get_or_create(name=tag_name.lower())
            PostHashtag.objects.create(post=self, hashtag=tag)
    
    def extract_and_save_mentions(self):
        # Extract mentions using regex
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, self.content)
        
        # Clear existing mentions
        self.mentions.all().delete()
        
        # Create new mentions
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                Mention.objects.create(post=self, user=user)
            except User.DoesNotExist:
                # Skip mentions of non-existent users
                pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Extract hashtags and mentions after saving
        self.extract_and_save_hashtags()
        self.extract_and_save_mentions()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Retweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='retweets')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='retweeted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} retweeted {self.post.id}"

class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"#{self.name}"

class PostHashtag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='hashtags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        unique_together = ('post', 'hashtag')
    
    def __str__(self):
        return f"{self.post.id} - {self.hashtag.name}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update hashtag post count
        if is_new:
            self.hashtag.post_count += 1
            self.hashtag.save()
    
    def delete(self, *args, **kwargs):
        # Update hashtag post count
        self.hashtag.post_count -= 1
        self.hashtag.save()
        super().delete(*args, **kwargs)

class Mention(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='mentions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentioned_in')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.post.id} mentions {self.user.username}"
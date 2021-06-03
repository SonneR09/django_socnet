from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', blank=True, null=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', blank=True, null=True,)
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)
    
    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='follower', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='following')
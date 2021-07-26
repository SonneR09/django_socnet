import rest_framework
from rest_framework.decorators import permission_classes
from .models import Post, Comment

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class PostSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']


class CommentSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author', 'post']

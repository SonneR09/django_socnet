from rest_framework.decorators import permission_classes
from .models import Follow, Post, Comment, Group
from users.serializers import UserSerializer

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated


class PostSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']


class CommentSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author', 'post']


class FollowerSerializer(serializers.ModelSerializer):
    permission_classes = (IsAuthenticated, )
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['title']

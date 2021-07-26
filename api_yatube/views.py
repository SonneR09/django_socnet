from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from posts.models import Post, Comment
from posts.pagination import CustomPagination
from users.serializers import UserSerializer
from posts.serializers import PostSerializer, CommentSerializer
from django.contrib.auth import get_user_model
from .permissions import IsAuthorOrReadOnlyPermission

User = get_user_model()

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    pagination_class = CustomPagination

    def create(self, request):
        if request.user.is_authenticated:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, pk=None):
        post = get_object_or_404(self.queryset, pk=pk)
        if request.user == post.author:
            serializer = self.serializer_class(post, data=request.data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        post = get_object_or_404(self.queryset, pk=pk)
        if request.user == post.author:
            serializer = self.serializer_class(post, data=request.data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        post = get_object_or_404(self.queryset, pk=pk)
        if request.user == post.author or request.user.is_superuser:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def list(self, request, post_id):
        queryset = Comment.objects.all().filter(post=post_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, post_id, pk):
        comment = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(comment)
        return Response(serializer.data)

    def create(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = self.serializer_class(data=request.data)
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, post_id, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = self.serializer_class(comment, data=request.data)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, post_id, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = self.serializer_class(comment, data=request.data)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class APIPostDetail(APIView):

#     def get(self, request, id):
#         post = get_object_or_404(Post, id=id)
#         serializer = PostSerializer(post)
#         return Response(serializer.data)

#     def put(self, request, id):
#         post = get_object_or_404(Post, id=id)
#         serializer = PostSerializer(post, data=request.data, partial=True)
#         if serializer.is_valid() and request.user.username == post.author.username:
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

#     def patch(self, request, id):
#         post = get_object_or_404(Post, id=id)
#         serializer = PostSerializer(post, data=request.data)
#         if serializer.is_valid() and request.user.username == post.author.username:
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, id):
#         post = get_object_or_404(Post, id=id)
#         if post.author.username == request.user.username:
#             post.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(status=status.HTTP_403_FORBIDDEN)


# @api_view(['GET', 'POST'])
# def api_posts(request):
#     if request.method == 'GET':
#         posts = Post.objects.all()
#         serializer = PostSerializer(posts, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     elif request.method == 'POST':
#         serializer = PostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

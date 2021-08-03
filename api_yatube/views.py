from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView
from rest_framework import filters

from posts.models import Group, Post, Comment, Follow
from users.serializers import UserSerializer
from posts.serializers import PostSerializer, CommentSerializer, FollowerSerializer, GroupSerializer
from .permissions import IsAuthorOrReadOnlyPermission
from .filters import PostFilter

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        username = self.kwargs.get('username', None)
        if username is not None:
            queryset = queryset.filter(username=username)
        return queryset


class PostListCreateAPIView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    filter_class = PostFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['text', 'author__username']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    filter_class = PostFilter
    filter_backends = (DjangoFilterBackend, )


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
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, post_id, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = self.serializer_class(comment, data=request.data)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, post_id, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        serializer = self.serializer_class(comment, data=request.data)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, post_id, pk=None):
        comment = get_object_or_404(Comment, pk=pk)

        if not request.user == comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListCreateAPIView(ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['=user__username', '=author__username']

    def perform_create(self, serializer):
        author_name = self.request.data.get("author", None)
        author = get_object_or_404(User, username=author_name)
        serializer.save(user=self.request.user, author=author)


class GroupListCreateAPIView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def perform_create(self, serializer):
        title = self.request.data.get('title', None)
        serializer.save(title=title)


# class PostViewSet(ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = (IsAuthorOrReadOnlyPermission, )
#     pagination_class = CustomPagination
#     filter_backends = [filters.OrderingFilter]
#     ordering_fields = ['pub_date', 'username']

#     def create(self, request):
#         if request.user.is_authenticated:
#             serializer = self.serializer_class(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(author=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_403_FORBIDDEN)

#     def partial_update(self, request, pk=None):
#         post = get_object_or_404(self.queryset, pk=pk)
#         if request.user == post.author:
#             serializer = self.serializer_class(post, data=request.data)
#             if serializer.is_valid():
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_403_FORBIDDEN)

#     def update(self, request, pk=None):
#         post = get_object_or_404(self.queryset, pk=pk)
#         if request.user == post.author:
#             serializer = self.serializer_class(post, data=request.data)
#             if serializer.is_valid():
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(status=status.HTTP_403_FORBIDDEN)

#     def destroy(self, request, pk=None):
#         post = get_object_or_404(self.queryset, pk=pk)
#         if request.user == post.author or request.user.is_superuser:
#             post.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_403_FORBIDDEN)

# class UserList(APIView):
#     """ Для фильтрации через APIView"""
#     permission_classes = (IsAuthorOrReadOnlyPermission, )

#     def get(self, request, username):
#         users = User.objects.filter(username=username)
#         serializer = UserSerializer(users, many=True)

#         return Response(serializer.data)

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

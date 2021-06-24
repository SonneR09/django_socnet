from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .serializers import PostSerializer
from posts import serializers


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {"page": page, "paginator": paginator})

@login_required()
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    auth_user = None
    following = False
    if request.user.is_authenticated:
        auth_user = get_object_or_404(User, username=request.user)
        if auth_user.follower.filter(author=author):
            following = True

    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "author": author,
        "page": page,
        "paginator": paginator,
        "following": following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = author.posts.get(pk=post_id)
    form = CommentForm()
    items = post.comments.all()

    following = False
    if request.user.is_authenticated:
        current_user = get_object_or_404(User, username=request.user)
        if Follow.objects.filter(user=current_user, author=author):
            following = True

    context = {"post": post, "form": form,
               "items": items, "following": following}
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    # добавим в form свойство files
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(
        request, 'new_post.html', {'form': form, 'post': post},
    )


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid:
            comment = form.save()
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', username=username, post_id=post_id)

    return render(request, 'comments.html', {"form": form, 'items': post, 'profile': profile})


@login_required
def follow_index(request):
    current_user = get_object_or_404(User, username=request.user)
    subscribes = current_user.follower.values_list('author')
    post_list = Post.objects.filter(
        author__in=subscribes).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        "follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    auth_user = get_object_or_404(User, username=request.user)
    user_to_follow = get_object_or_404(User, username=username)

    Follow.objects.create(user=auth_user, author=user_to_follow)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    auth_user = get_object_or_404(User, username=request.user)
    user_to_unfollow = get_object_or_404(User, username=username)

    follow = get_object_or_404(Follow, user=auth_user, author=user_to_unfollow)
    follow.delete()

    return redirect('profile', username=username)


def get_post(request, id):
    post = get_object_or_404(Post, id=id)
    serializer = PostSerializer(post)
    return JsonResponse(serializer.data)


@api_view(['GET', 'POST'])
def api_posts(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
         serializer = PostSerializer(data=request.data)
         if serializer.is_valid():
             serializer.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
     "index.html", 
     {"page":page, "paginator":paginator}
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {"page":page, "paginator":paginator})


@login_required()
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form':form})
    
    form = PostForm()
    return render(request, 'new_post.html', {'form':form})


def profile(request, username):
        author = get_object_or_404(User, username=username)
        auth_user = None
        if request.user.is_authenticated:
            auth_user = request.user.username
        posts = author.posts.all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {
            "author":author, 
            "auth_user":auth_user,
            "page":page,
            "paginator":paginator
            }
        return render(request, 'profile.html', context)
 
 
def post_view(request, username, post_id):
        author = get_object_or_404(User, username=username)
        post = author.posts.get(id=post_id)
        context = {"author":author, "post":post}
        return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
        post = get_object_or_404(Post, pk=post_id)
        auth_username = request.user
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)

            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect('profile', username=username)
        else:
            form = PostForm(instance=post)
            context = {"post":post, "auth_username":auth_username, "form":form}
        return render(request, 'new_post.html', context)


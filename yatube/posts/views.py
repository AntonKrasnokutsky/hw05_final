from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Group, Post, Follow
from .forms import PostForm, CommentForm


POSTS_PER_PAGE = 10


def pagintor(posts, page, post_per_page=POSTS_PER_PAGE):
    pagintor = Paginator(posts, post_per_page)
    page_obj = pagintor.get_page(page)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all().select_related()
    page_obj = pagintor(posts, request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """
    Сообщества
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = pagintor(posts, request.GET.get('page'))
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    User = get_user_model()
    author = User.objects.get(username=username)
    posts = author.posts.all()
    page_obj = pagintor(posts, request.GET.get('page'))
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user)
    else:
        following = False

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:profile', request.user.username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save(commit=False).save()
        return redirect('posts:post_detail', post.id)
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups,
        'post_id': post_id,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    # Получите пост
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        post = get_object_or_404(Post, pk=post_id)
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followings = request.user.follower.all()
    authors = []
    for following in followings:
        authors.append(following.author)
    posts = Post.objects.filter(author__in=authors)
    page_obj = pagintor(posts, request.GET.get('page'))
    context = {'page_obj': page_obj, }
    return render(request, 'posts/index.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    User = get_user_model()
    author = get_object_or_404(User, username=username)
    if author != request.user:
        if not author.following.filter(user=request.user):
            Follow.objects.create(
                user=request.user,
                author=author,
            )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    User = get_user_model()
    author = get_object_or_404(User, username=username)
    author.following.get(user=request.user).delete()
    return redirect('posts:profile', username)

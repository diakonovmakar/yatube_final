from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import set_up_paginator

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def index(request):
    post_list = cache.get('index_page')
    if post_list is None:
        post_list = Post.objects.select_related(
            'group',
            'author').order_by('-pub_date')
        cache.set('index_page', post_list, timeout=20)

    paginator = set_up_paginator(post_list)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'

    context = {'posts': post_list, 'page': page, 'title': title}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    paginator = set_up_paginator(post_list)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    title = f'Записи сообщества {group}'
    header = group

    context = {
        'posts': post_list,
        'page': page,
        'group': group,
        'title': title,
        'header': header}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all().order_by('-pub_date')
    count = user.posts.all().count()
    paginator = set_up_paginator(post_list)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    title = f'Записи пользователя {user}.'

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=user,
            user=request.user).exists()

    context = {
        'author': user,
        'count': count,
        'posts': post_list,
        'page': page,
        'title': title,
        'following': following}
    return render(request, 'posts/profile.html', context)


def post_detail(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    title = post.text[:30]
    comments = post.comments.all().order_by('-created')
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=username)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = user
        comment.post = post
        form.save()
        return redirect(
            'post:post_detail',
            username=user.username,
            post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'comments': comments,
        'title': title,
        'is_comment': True}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        text = form.save(commit=False)
        text.author = request.user
        text.save()
        return redirect('post:index')
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, username, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    if user != author:
        return redirect(
            'post:post_detail',
            username=author.username,
            post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'post:post_detail',
            username=author.username,
            post_id=post_id)
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=username)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = user
        comment.post = post
        form.save()
        return redirect(
            'post:post_detail',
            username=user.username,
            post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_comment': True}
    return render(request, 'posts/post_detail.html', context)


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(
        author__following__user=user).order_by('-pub_date')
    paginator = set_up_paginator(post_list)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    title = 'Избранные авторы'

    context = {'posts': post_list, 'page': page, 'title': title}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('post:profile', username=(author.username))


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('post:profile', username=(author.username))

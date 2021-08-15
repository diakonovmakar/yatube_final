from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст'
    )
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True,

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',

    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        blank=True,
        null=True
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Ваш комментарий'
    )
    created = models.DateTimeField(
        'comment_date',
        auto_now_add=True
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )


class Group(models.Model):
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        unique=True
    )
    description = models.TextField()

    def __str__(self) -> str:
        return self.title

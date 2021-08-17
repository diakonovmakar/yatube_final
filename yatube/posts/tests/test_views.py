from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='MakarD')
        cls.user2 = User.objects.create(username='AndreyG')
        cls.group = Group.objects.create(
            title='Black',
            slug='black',
            description='Test description'
        )
        cls.user2_post = Post.objects.create(
            text='bla-bla-bla2',
            author=cls.user2,
            group=cls.group
        )
        cls.post = Post.objects.create(
            text='bla-bla-bla',
            author=cls.user,
            group=cls.group
        )

    def setUp(self) -> None:
        self.user = PostsPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = PostsPagesTests.user.username
        self.slug = PostsPagesTests.group.slug
        self.post_id = PostsPagesTests.post.pk

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('post:index'): 'index.html',
            reverse(
                'post:group_list',
                kwargs={'slug': self.slug}): 'posts/group_list.html',
            reverse(
                'post:profile',
                kwargs={'username': self.username}): 'posts/profile.html',
            reverse('post:post_detail', kwargs={
                'username': self.user.username,
                'post_id': self.post_id}): 'posts/post_detail.html',
            reverse('post:post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post_id}): 'posts/create_post.html',
            reverse('post:post_create'): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_shows_correct_context(self):
        """Шаблоны приложения posts/ сформированы с правильным контекстом."""
        cache.delete('index_page')
        reverses_pages = [
            reverse('post:index'),
            reverse(
                'post:group_list',
                kwargs={'slug': self.slug}),
            reverse(
                'post:profile',
                kwargs={'username': self.username}),
            reverse('post:post_detail', kwargs={
                'username': PostsPagesTests.user.username,
                'post_id': PostsPagesTests.post.pk}),
        ]
        for reverse_name in reverses_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                try:
                    first_object = response.context['page'][0]
                except KeyError:
                    first_object = response.context['post']
                post_text_0 = first_object.text
                post_author_0 = first_object.author
                post_group_0 = first_object.group
                self.assertEqual(post_text_0, PostsPagesTests.post.text)
                self.assertEqual(post_author_0, PostsPagesTests.user)
                self.assertEqual(post_group_0, PostsPagesTests.group)

    def test_create_page_show_correct_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        reverses_pages = [
            reverse(
                'post:post_edit',
                kwargs={
                    'username': PostsPagesTests.user.username,
                    'post_id': self.post_id}),
            reverse('post:post_create')
        ]
        for reverse_name in reverses_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_cache_index(self):
        response = self.authorized_client.get(reverse('post:index'))
        first = response.context['posts'][0]
        new_first = Post.objects.create(
            text='bla-bla-bla',
            author=PostsPagesTests.user,
            group=PostsPagesTests.group
        )

        new_response = self.authorized_client.get(reverse('post:index'))
        self.assertEqual(new_response.context['posts'][0], first)
        cache.delete('index_page')
        new_response = self.authorized_client.get(reverse('post:index'))
        self.assertEqual(new_response.context['posts'][0], new_first)

    def test_follow(self):
        not_follow_index_response = self.authorized_client.get(reverse(
            'post:follow_index'))

        self.assertEqual(
            len(not_follow_index_response.context['page']), 0)
        self.authorized_client.get(
            reverse(
                'post:profile_follow',
                kwargs={'username': PostsPagesTests.user2.username}))
        follow_index_response = self.authorized_client.get(
            reverse('post:follow_index'))

        self.assertEqual(
            len(follow_index_response.context['page']), 1)
        self.assertEqual(
            follow_index_response.context['page'][0].author,
            PostsPagesTests.user2
        )

    def test_unfollow(self):
        self.authorized_client.get(
            reverse(
                'post:profile_follow',
                kwargs={'username': PostsPagesTests.user2.username}))
        follow_index_response = self.authorized_client.get(
            reverse('post:follow_index'))
        self.assertEqual(
            len(follow_index_response.context['page']), 1)

        self.authorized_client.get(
            reverse(
                'post:profile_unfollow',
                kwargs={'username': PostsPagesTests.user2.username}))
        not_follow_index_response = self.authorized_client.get(
            reverse('post:follow_index'))
        self.assertEqual(
            len(not_follow_index_response.context['page']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='MakarD')
        for i in range(13):
            Post.objects.create(
                text='bla-bla-bla' + str(i),
                author=cls.user
            )

    def test_first_page_contains_ten_records(self):
        cache.delete('index_page')
        response = self.client.get(reverse('post:index'))
        self.assertEqual(len(response.context['page']), 10)

    def test_second_page_contains_three_records(self):
        cache.delete('index_page')
        response = self.client.get(reverse('post:index') + '?page=2')
        self.assertEqual(len(response.context['page']), 3)

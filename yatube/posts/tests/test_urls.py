from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Black',
            slug='black',
            description='Test description'
        )
        cls.user = User.objects.create_user(username='MakarD')
        cls.post = Post.objects.create(
            text='BlaBlaBla',
            author=cls.user,
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_http_statuses(self):
        username = PostsURLTests.user.username
        group = PostsURLTests.group
        post_id = PostsURLTests.post.pk
        templates_codes = {
            '/': {
                'code': HTTPStatus.OK.value,
                'is_logined': False},
            f'/group/{group.slug}/': {
                'code': HTTPStatus.OK.value,
                'is_logined': False},
            f'/{username}/': {
                'code': HTTPStatus.OK.value,
                'is_logined': False},
            f'/{username}/{post_id}/': {
                'code': HTTPStatus.OK.value,
                'is_logined': False},
            f'/{username}/{post_id}/edit/': {
                'code': HTTPStatus.OK.value,
                'is_logined': True},
            '/new/': {
                'code': HTTPStatus.OK.value,
                'is_logined': True},
            '/unexisting_page/': {
                'code': HTTPStatus.NOT_FOUND.value,
                'is_logined': False},
        }

        for adress, values in templates_codes.items():
            with self.subTest(adress=adress):
                if values['is_logined']:
                    response = self.authorized_client.get(adress)
                else:
                    response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, values['code'])

    def test_redirect_from_create_post(self):
        response = self.guest_client.get('/new/')
        self.assertRedirects(
            response, '/auth/login/?next=/new/'
        )

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        username = PostsURLTests.user.username
        group = PostsURLTests.group
        post_id = PostsURLTests.post.pk
        templates_url_names = {
            '/': 'index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/{username}/': 'posts/profile.html',
            f'/{username}/{post_id}/': 'posts/post_detail.html',
            f'/{username}/{post_id}/edit/': 'posts/create_post.html',
            '/new/': 'posts/create_post.html'
        }

        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

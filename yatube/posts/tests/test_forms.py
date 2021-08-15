import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube import settings

from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='MakarD')
        cls.group = Group.objects.create(
            title='Black',
            slug='black',
            description='Test description'
        )
        cls.post = Post.objects.create(
            text='bla-bla-bla',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = PostCreateFormTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'TL;DR',
            'group': PostCreateFormTest.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('post:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('post:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            image='posts/small.gif').exists())

    def test_post_edit_form(self):
        post = PostCreateFormTest.post
        form_data = {
            'text': 'CatDogCat',
            'group': PostCreateFormTest.group.pk
        }
        response = self.authorized_client.post(
            reverse('post:post_edit', kwargs={
                'username': PostCreateFormTest.user.username,
                'post_id': post.pk}),
            data=form_data
        )
        post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('post:post_detail', kwargs={
                'username': PostCreateFormTest.user.username,
                'post_id': post.pk}))
        self.assertEqual(PostCreateFormTest.post.text, form_data['text'])
        self.assertEqual(PostCreateFormTest.post.group.pk, form_data['group'])

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='MakarD')
        cls.post = Post.objects.create(
            text='0123456789ABCDEF',
            author=cls.user
        )

        cls.group = Group.objects.create(
            title='Black',
            slug='black',
            description='Test description'
        )

    def test_post(self):
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(
            expected_object_name,
            PostsModelTest.post.text[:15],
            'Method __str__ is working wrong in "Post" class')

    def test_group(self):
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(
            expected_object_name,
            'Black',
            'Method __str__ is working wrong in "Group" class')

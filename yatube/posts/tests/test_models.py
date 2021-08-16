from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Follow, Group, Post

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


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='MakarD')
        cls.user2 = User.objects.create_user(username='AndreyG')
        cls.follow = Follow.objects.create(
            user=FollowModelTest.user1,
            author=FollowModelTest.user2)

    def test_follow(self):
        expected_follow = Follow.objects.filter(
            author=FollowModelTest.follow.author,
            user=FollowModelTest.follow.user).get()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(FollowModelTest.follow.author, expected_follow.author)
        self.assertEqual(FollowModelTest.follow.user, expected_follow.user)

    def test_unfollow(self):
        Follow.objects.filter(
            author=FollowModelTest.follow.author,
            user=FollowModelTest.follow.user).delete()
        self.assertEqual(Follow.objects.count(), 0)
        self.assertFalse(Follow.objects.filter(
            author=FollowModelTest.follow.author,
            user=FollowModelTest.follow.user).exists())

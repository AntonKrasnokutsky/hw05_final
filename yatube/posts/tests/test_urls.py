from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='author')
        cls.another_author = User.objects.create_user(username='another')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)

        cls.group = Group.objects.create(
            title='Название группы',
            slug='group-slag',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Пост в тесте!!!' * 20,
            author=cls.author,
        )

    def setUp(self, *args, **kwargs):
        cache.clear()

    def test_guest_url_exists_at_desired_location(self):
        guest_url_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug,
                }): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.author.username,
                }): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id,
                }): HTTPStatus.FOUND,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id,
                }): HTTPStatus.OK,
            'unexisting_page': HTTPStatus.NOT_FOUND,
        }
        for address, status_code in guest_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_author_user_url_exists_at_desired_location(self):
        authorized_url_names = {
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id,
                }): HTTPStatus.OK,
        }
        for address, status_code in authorized_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_another_author_user_url_exists_at_desired_location(self):
        authorized_url_names = {
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id,
                }): HTTPStatus.FOUND,
        }
        for address, status_code in authorized_url_names.items():
            with self.subTest(address=address):
                response = self.another_author_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug,
                }): 'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.author.username,
                }): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id,
                }): 'posts/create_post.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id,
                }): 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

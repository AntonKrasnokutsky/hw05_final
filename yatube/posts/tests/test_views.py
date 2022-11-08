import shutil
import tempfile
from http import HTTPStatus
from itertools import islice

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.other_author = User.objects.create_user(username='other_author')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='group-slag',
            description='Описание группы',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        batch_size = 15
        objs = (
            Post(
                text=('Пост %s в тесте!!!' % number_post) * 20,
                group=cls.group,
                author=cls.user,
                image=cls.uploaded,
            )
            for number_post in range(batch_size)
        )
        posts = list(islice(objs, batch_size))
        Post.objects.bulk_create(posts, batch_size)

        cls.post = Post.objects.first()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self, *args, **kwargs):
        cache.clear()
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.other_client = Client()
        self.other_client.force_login(self.other_author)
        self.author_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.other_author.username,
                },
            ))

    def test_guest_page_accessible_by_name(self, *args, **kwargs):
        """URLs, генерируемые при помощи имён, доступны всем."""
        guest_urls_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug,
            }): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': self.user.username,
            }): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id,
            }): HTTPStatus.OK,
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id,
            }): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id,
            }): HTTPStatus.FOUND,
        }
        for reverse_name, status_code in guest_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.guest_client.get(reverse_name)
                self.assertEqual(respose.status_code, status_code)

    def test_author_page_accessible_by_name(self, *args, **kwargs):
        """URLs, генерируемые при помощи имён, доступны всем."""
        author_urls_names = {
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id,
            }): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
        }
        for reverse_name, status_code in author_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.author_client.get(reverse_name)
                self.assertEqual(respose.status_code, status_code)

    def test_guest_page_uses_correct_template(self, *args, **kwargs):
        """При запросе по имени применяются правильные шаблоны."""
        guest_urls_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug,
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user.username,
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id,
            }): 'posts/post_detail.html',
        }
        for reverse_name, template in guest_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(respose, template)

    def test_author_page_uses_correct_template(self, *args, **kwargs):
        """При запросе по имени применяются правильные шаблоны."""
        author_urls_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id,
            }): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/index.html',
        }
        for reverse_name, template in author_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.author_client.get(reverse_name)
                self.assertTemplateUsed(respose, template)

    def test_index_page_show_correct_context(self, *args, **kwargs):
        """Контекст содержит список постов."""
        response = self.guest_client.get(reverse('posts:index'))
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)
            self.assertIsNotNone(post.image)

    def test_group_list_page_show_correct_context(self, *args, **kwargs):
        """Контекст содержит список постов отфильтрованных по группе."""
        reverse_name = reverse(
            'posts:group_list',
            kwargs={
                'slug': self.group.slug,
            })
        response = self.guest_client.get(reverse_name)
        self.assertEqual(response.context['group'], self.group)
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.group, self.group)
            self.assertIsNotNone(post.image)

    def test_profile_page_show_correct_context(self, *args, **kwargs):
        """Контекст содержит список постов отфильтрованных по группе."""
        reverse_name = reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username,
            })
        response = self.guest_client.get(reverse_name)
        self.assertEqual(response.context['author'], self.user)
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author, self.user)
            self.assertIsNotNone(post.image)

    def test_post_detail_page_show_correct_context(self, *args, **kwargs):
        """Контекст содержит список постов отфильтрованных по группе."""
        reverse_name = reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post.id,
            })
        response = self.guest_client.get(reverse_name)
        self.assertEqual(response.context['posts_count'], 15)
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, self.post.id)
        self.assertIsNotNone(post.image)

    def test_post_create_page_show_correct_context(self, *args, **kwargs):
        """Шаблон post_create сформирован с правльным контекстом."""
        reverse_name = reverse('posts:post_create')
        response = self.author_client.get(reverse_name)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        for group in response.context.get('groups'):
            self.assertIsInstance(group, Group)

    def test_post_edit_page_show_correct_context(self, *args, **kwargs):
        """Шаблон post_create сформирован с правльным контекстом."""
        reverse_name = reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post.id,
            })
        response = self.author_client.get(reverse_name)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        for group in response.context.get('groups'):
            self.assertIsInstance(group, Group)
        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('post_id'), self.post.id)

    def test_paginator_page_contains_records(self, *args, **kwargs):
        """Проверка: количество постов на страницах."""
        first_list_paginator = {
            self.guest_client.get(reverse('posts:index')): 10,
            self.guest_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug},
                )): 10,
            self.guest_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username},
                )): 10,
            self.guest_client.get(reverse('posts:index'), {'page': 2}): 5,
            self.guest_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug},
                ), {'page': 2}): 5,
            self.guest_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username},
                ), {'page': 2}): 5,
        }
        for response, count in first_list_paginator.items():
            self.assertEqual(len(response.context['page_obj']), count)

    def test_new_post_page_contains_three_records(self, *args, **kwargs):
        new_group = Group.objects.create(
            title='Новая группы',
            slug='new-group',
            description='Описание новой группы',
        )
        new_post = Post.objects.create(
            text='Новый пост в тесте!!!',
            group=new_group,
            author=self.user,
        )
        first_list_paginator = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': new_group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        ]
        for reverse_name in first_list_paginator:
            response = self.guest_client.get(reverse_name)
            self.assertEqual(response.context['page_obj'][0], new_post)

    def test_new_comment_contains_three_records(self, *args, **kwargs):
        new_post = Post.objects.create(
            text='Новый пост в тесте!!!',
            author=self.user,
        )
        new_comment = Comment.objects.create(
            post=new_post,
            author=self.user,
            text='Тестовый комментарий на странице.'
        )

        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': new_post.id,
                }))
        self.assertEqual(response.context['comments'][0], new_comment)

    def test_index_page_in_cache(self, *args, **kwargs):
        response = self.client.get(reverse('posts:index'))
        post = Post.objects.latest('created')
        Post.objects.latest('created').delete()
        self.assertIn(post.text.encode('utf-8'), response.content)

    def test_index_page_clear_cache(self, *args, **kwargs):
        response = self.client.get(reverse('posts:index'))
        post = Post.objects.latest('created')
        Post.objects.latest('created').delete()
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotIn(post.text.encode('utf-8'), response.content)

    def test_add_follow(self, *args, **kwargs):
        count = Follow.objects.all().count()
        self.other_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.user.username,
                }
            ))
        new_count = Follow.objects.all().count()
        self.assertEqual(new_count, count + 1)
        new_follow = Follow.objects.last()
        self.assertEqual(new_follow.user, self.other_author)
        self.assertEqual(new_follow.author, self.user)

    def test_remove_follow(self, *args, **kwargs):
        count = Follow.objects.all().count()
        self.author_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.other_author.username,
                }))
        new_count = Follow.objects.all().count()
        self.assertEqual(new_count, count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.other_author
            ).exists())

    def test_new_post_followin_in_tape(self, *args, **kwargs):
        self.other_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.user.username,
                }))
        new_post = Post.objects.create(
            text='Новый пост в тесте подписок!!!',
            author=self.user,
        )
        response = self.other_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0], new_post)

        response = self.author_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

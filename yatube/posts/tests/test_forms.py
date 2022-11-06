import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных
        cls.user = User.objects.create_user(username="author")
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Пост в тесте forms!!!',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self, *args, **kwargs):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.filter(author=self.user).count()
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
            'text': 'Тестовый текст для увеличесния количества записей',
            'image': uploaded,
        }

        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # Проверяем, увеличилось ли число постов
        new_post_count = Post.objects.filter(author=self.user).count()
        self.assertEqual(new_post_count, post_count + 1)

        new_post = Post.objects.latest('created')
        uploaded = f'posts/{uploaded}'
        self.assertEqual(new_post.group, None)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.image, uploaded)

    def test_edit_post(self):
        """Валидная форма редактирования запись в Post."""
        # Подсчитаем количество записей в Post
        post_count = Post.objects.filter(author=self.user).count()
        form_data = {
            'text': 'Тестовый текст для редактирования записей',
            # Все посты в базе без группы. Добавляем группу
            'group': self.group.id,
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.id,
                }),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов.
        new_post_count = Post.objects.filter(author=self.user).count()
        self.assertEqual(new_post_count, post_count)
        # Проверяем, сохранились ли изменения.
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        # Проверяем, добавилась ли группа
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)

    def test_create_comment_authorized_user(self, *args, **kwargs):
        post = Post.objects.last()
        comment_count = post.comments.all().count()
        form_data = {
            'text': 'Тестовый комментарий.',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': post.id,
                }),
            data=form_data,
            follow=True,
        )
        new_comments_count = post.comments.all().count()
        self.assertEqual(new_comments_count, comment_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': post.id,
                }))

    def test_create_comment_guest_user(self, *args, **kwargs):
        post = Post.objects.last()
        comment_count = post.comments.all().count()
        form_data = {
            'text': 'Тестовый комментарий.',
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': post.id,
                }),
            data=form_data,
            follow=True,
        )
        new_comments_count = post.comments.all().count()
        self.assertEqual(new_comments_count, comment_count)

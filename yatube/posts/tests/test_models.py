from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название группы',
            slug='Слаг группы',
            description='Описание группы',
        )
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Пост в тесте!!!' * 20,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        post = PostModelsTest.post
        group = PostModelsTest.group
        value_class_str = {
            post: 'Пост в тесте!!!',
            group: 'Название группы',
        }
        for obj, value in value_class_str.items():
            with self.subTest(obj=obj):
                self.assertEqual(
                    obj.__str__(),
                    value,
                    f'В модели {obj.__class__.__name__} '
                    'функция __str__() работает неправильно',
                )

    def test_models_post_verbose_name(self):
        post = PostModelsTest.post
        field_verboses_post = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_models_group_verbose_name(self):
        group = PostModelsTest.group
        field_verboses_group = {
            'title': 'Название группы',
            'slug': 'Slag группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_models_post_help_text(self):
        post = PostModelsTest.post
        field_help_text_post = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_models_group_help_text(self):
        group = PostModelsTest.group
        field_help_text_group = {
            'title': 'Введите название группы',
            'slug': 'Введите slug группы',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_text_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

from http import HTTPStatus

from django import forms
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersViewsTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.user = User.objects.create_user(username='author')
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_guest_page_accessible_by_name(self, *args, **kwargs):
        """URLs, генерируемые при помощи именён, доступны всем."""
        guest_urls_names = {
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
        }
        for reverse_name, status_code in guest_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.guest_client.get(reverse_name)
                self.assertEqual(respose.status_code, status_code)

    def test_author_page_accessible_by_name(self, *args, **kwargs):
        """URLs, генерируемые при помощи именён, доступны авторизованному
            пользователю. """
        guest_urls_names = {
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for reverse_name, status_code in guest_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.author_client.get(reverse_name)
                self.assertEqual(respose.status_code, status_code)

    def test_guest_page_uses_correct_template(self, *args, **kwargs):
        """При запросе по имени применяются правильные шаблоны."""
        guest_urls_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in guest_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(respose, template)

    def test_author_page_uses_correct_template(self, *args, **kwargs):
        """URLs, генерируемые при помощи именён, доступны. """
        author_urls_names = {
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in author_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.author_client.get(reverse_name)
                self.assertTemplateUsed(respose, template)

    def test_signup_pages_show_correct_context(self, *args, **kwargs):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

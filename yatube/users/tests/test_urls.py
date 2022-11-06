from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersUrlsTest(TestCase):
    def setUp(self):
        super().setUpClass()
        self.guest_client = Client()
        self.author = User.objects.create_user(username='author')
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_guest_url_exists_at_desired_location(self):
        """URLs гостя доступны"""
        urls_names = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
        }
        for reverse_name, status_code in urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    response.status_code,
                    status_code,
                    reverse_name,
                )

    def test_author_url_exists_at_desired_location(self):
        """URLs авторизованного пользователя доступны"""
        urls_names = {
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for reverse_name, status_code in urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    response.status_code,
                    status_code,
                    reverse_name,
                )

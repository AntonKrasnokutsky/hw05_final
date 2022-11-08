from http import HTTPStatus

from django.test import Client, TestCase


class CoreViewsTests(TestCase):
    def setUp(self, *args, **kwargs):
        self.guest_client = Client()

    def test_error_page(self, *args, **kwargs):
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

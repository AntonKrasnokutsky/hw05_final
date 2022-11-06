from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_accessible_by_name(self, *args, **kwargs):
        """URLs, генерируемые при помощи именён доступны и используют
            правильыне шаблоны."""
        urls_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                respose = self.guest_client.get(reverse_name)
                self.assertEqual(respose.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(respose, template)

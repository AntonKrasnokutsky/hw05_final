from django.test import TestCase
from django.urls import reverse


class AboutUrlsTest(TestCase):
    def test_urls_uses_correct_name(self):
        templates_url_names = {
            reverse('about:author'): '/about/author/',
            reverse('about:tech'): '/about/tech/',
        }
        for reverse_name, path in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse_name, path)

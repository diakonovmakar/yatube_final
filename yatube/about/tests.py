from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_views_use_correct_template(self):
        adress_template = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for adress, template in adress_template.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_http_statuses_views(self):
        path_code = {
            reverse('about:author'): HTTPStatus.OK.value,
            reverse('about:tech'): HTTPStatus.OK.value
        }
        for adress, code in path_code.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code)


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_urls_use_correct_template(self):
        adress_template = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for adress, template in adress_template.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_http_statuses_urls(self):
        url_codes = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value
        }
        for adress, code in url_codes.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, code)

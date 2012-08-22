from django.test import SimpleTestCase
from django.test.client import Client
from django.test.utils import override_settings


class TestFileserverViews(SimpleTestCase):
    def setUp(self):
        self.c = Client()

    def test_front_page(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

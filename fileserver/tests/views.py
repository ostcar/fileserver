from django.test import SimpleTestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.core.files.storage import default_storage

from ..utils.filesystem import Directory


class TestFileserverViews(SimpleTestCase):
    def setUp(self):
        self.c = Client()

    def test_front_page(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    @override_settings(LOGIN_PASSWORD='PASSWORD')
    def test_login(self):
        response = self.c.get('/login/')
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/login/', {'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].errors['password'],
                         [u'Wrong password'])
        response = self.c.post('/login/', {'password': 'PASSWORD'})
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        response = self.c.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'],
                         'http://testserver/')

    def test_directory(self):
        response = self.c.get('/index/')
        self.assertEqual(response.status_code, 200)
        directory = Directory('')
        self.assertEqual(response.context['directory'].path, directory.path)

    def test_create_subdirectory(self):
        response = self.c.post('/mkdir/',
                               {'name': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(default_storage.exists('test'))
        default_storage.delete('test')



from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
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

    def test_download(self):
        response = self.c.get('/download/test_file1.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'The first test file.\n')

    def test_zip_directory(self):
        response = self.c.get('/zip/')
        self.assertEqual(response.status_code, 200)

    def test_upload(self):
        new_file = SimpleUploadedFile('new_file', 'content')
        response = self.c.post('/upload/',
                               {'form-TOTAL_FORMS':1,
                                'form-INITIAL_FORMS': 0,
                                'form-0-file': new_file})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(default_storage.exists('new_file'))
        default_storage.delete('new_file')

    def test_update_directory(self):
        test_file2 = ContentFile('content\n')
        default_storage.save('test_file2', test_file2)
        default_storage.mkdir('test_dir')
        response = self.c.post('/edit/',
                               {'form-TOTAL_FORMS': 3,
                                'form-INITIAL_FORMS': 3,
                                'form-0-old_name': 'test_file1.txt',
                                'form-0-new_name': 'test_file1.renamed',
                                'form-1-old_name': 'test_file2',
                                'form-1-new_name': 'test_file2',
                                'form-1-DELETE': True,
                                'form-2-old_name': 'test_dir',
                                'form-2-new_name': 'test_dir',
                                'form-2-DELETE': True})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(default_storage.exists('test_file2'))
        self.assertFalse(default_storage.exists('test_file1.txt'))
        self.assertFalse(default_storage.exists('test_dir'))
        self.assertTrue(default_storage.exists('test_file1.renamed'))
        default_storage.mv('test_file1.renamed', 'test_file1.txt')

    def test_not_empty_directory(self):
        default_storage.mkdir('not_empty_dir')
        test_file2 = ContentFile('content\n')
        default_storage.save('not_empty_dir/test_file2', test_file2)
        response = self.c.post('/edit/',
                               {'form-TOTAL_FORMS': 1,
                                'form-INITIAL_FORMS': 1,
                                'form-0-old_name': 'not_empty_dir',
                                'form-0-new_name': 'not_empty_dir',
                                'form-0-DELETE': True})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(default_storage.exists('not_empty_dir'))




    def test_todo(self):
        response = self.c.get('/todo/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['todo'].value(), '')
        response = self.c.post('/todo/',
                               {'todo': 'new_content\n'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(default_storage.open('todo.txt').read(), 'new_content\n')

        response = self.c.get('/todo/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['todo'].value(), 'new_content\n')

        default_storage.delete('todo.txt')




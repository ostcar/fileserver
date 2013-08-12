import os

from django.test import SimpleTestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.core.files.storage import default_storage




class TestFileServerStorage(SimpleTestCase):
    def test_extra_methodes(self):
        default_storage.mkdir('test_directory')
        self.assertTrue(default_storage.exists('test_directory'))

        default_storage.mv('test_directory', 'moved_directory')
        self.assertTrue(default_storage.exists('moved_directory'))

        default_storage.delete('moved_directory')
        self.assertFalse(default_storage.exists('moved_directory'))



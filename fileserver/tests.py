from StringIO import StringIO

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.core.files.storage import default_storage


class TestUtilsFilesystem(TestCase):
    def setUp(self):
        self.file1 = StringIO("The first File")
        self.file2 = StringIO("The second File")

    @override_settings(MEDIA_ROOT='/tmp/fileserver_test_content')
    def test_fileserver_storage(self):
        default_storage.save("file1", self.file1)
        self.assertTrue(default_storage.exists("file1"))



import fake_filesystem
import fake_filesystem_shutil

from django.core.files.storage import Storage
from django.test.simple import DjangoTestSuiteRunner
from django.core.files.base import ContentFile

from ..utils.filesystem import FileServerStorage


class FileServerTestSuiteRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        #old_config = self.setup_databases()
        result = self.run_suite(suite)
        #self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)


class FakeMemoryStorage(FileServerStorage):
    """
    Django storage class for in-memory filesystem.
    """
    def __init__(self, filesystem=None):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os = fake_filesystem.FakeOsModule(self.filesystem)
        self._open = fake_filesystem.FakeFileOpen(self.filesystem)
        self.shutil = fake_filesystem_shutil.FakeShutilModule(self.filesystem)

    def path(self, name):
        return "/%s" % name

    def _save(self, path, content):
        if isinstance(content, ContentFile):
            content = content.read()
        self.filesystem.CreateFile(path, contents=content)
        return path

    def exists(self, name):
        if name == '':
            return True
        return self.os.path.exists(name)

    def size(self, name):
        return self.os.path.getsize(self.path(name))

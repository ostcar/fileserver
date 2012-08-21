# -*- coding: utf-8 -*-
import os

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse


class Directory(object):
    def __init__(self, path):
        self.path = path
        self.subdirectories, self.files = default_storage.listdir(path)

    def iter_subdirectories(self):
        for subdirectory in self.subdirectories:
            if subdirectory.startswith('.'):
                continue
            subsubdirectory, subfiles = default_storage.listdir(
                os.path.join(self.path, subdirectory))
            item_count = len(subsubdirectory) + len(subfiles)
            subdirectory_url = reverse('fileserver_directory', args=[os.path.join(
                self.path, subdirectory)])
            yield (subdirectory, subdirectory_url, item_count)

    def iter_files(self):
        for file in self.files:
            if file.startswith('.'):
                continue
            path_to_file = os.path.join(self.path, file)
            size = default_storage.size(path_to_file)
            file_url = default_storage.url(path_to_file)
            yield (file, file_url, size)

    def __repr__(self):
        return unicode(self.path)


def save_file(path, file):
    # TODO normalize filename
    name = os.path.join(path, file.name)
    default_storage.save(name, file)

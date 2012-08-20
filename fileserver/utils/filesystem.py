# -*- coding: utf-8 -*-
import os

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse


class Folder(object):
    def __init__(self, path):
        self.path = path
        self.subfolders, self.files = default_storage.listdir(path)

    def iter_subfolders(self):
        for subfolder in self.subfolders:
            if subfolder.startswith('.'):
                continue
            subsubfolders, subfiles = default_storage.listdir(
                os.path.join(self.path, subfolder))
            item_count = len(subsubfolders) + len(subfiles)
            subfolder_url = reverse('fileserver_folder', args=[os.path.join(
                self.path, subfolder)])
            yield (subfolder, subfolder_url, item_count)

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

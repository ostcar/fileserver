# -*- coding: utf-8 -*-
import os
import shutil
import urllib
import mimetypes
from zipfile import ZipFile, ZIP_DEFLATED
from contextlib import closing

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

from django.core.urlresolvers import reverse

extensions_map = mimetypes.types_map.copy()
extensions_map.update({
    '': 'application/octet-stream', # Default
    '.py': 'text/plain',
    '.c': 'text/plain',
    '.h': 'text/plain'})


class FileServerStorage(FileSystemStorage):
    def mkdir(self, path):
        os.mkdir(self.path(path))

    def mv(self, old_path, new_path):
        new_path = self.get_available_name(new_path)
        os.rename(self.path(old_path), self.path(new_path))

    def delete(self, name):
        if os.path.isdir(self.path(name)):
            shutil.rmtree(self.path(name))
        else:
            os.remove(self.path(name))

    # From http://stackoverflow.com/a/296722
    def zipdir(self, basedir, archivename, include_hidden=False):
        path = self.path(basedir)
        assert os.path.isdir(path)
        with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as archiv:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if include_hidden or not file.startswith('.'):
                        abs_path = os.path.join(root, file)
                        relative_path = abs_path[len(path) + len(os.sep):]
                        archiv.write(abs_path, relative_path)


class Directory(object):
    def __init__(self, path, sort='size', reverse=False):
        self.path = path
        subdirectories, files = default_storage.listdir(path)

        self.subdirectories = []
        for subdirectory in subdirectories:
            if subdirectory.startswith('.'):
                continue
            subsubdirectory, subfiles = default_storage.listdir(
                os.path.join(self.path, subdirectory))
            item_count = len(subsubdirectory) + len(subfiles)
            self.subdirectories.append((subdirectory, item_count))

        self.files = []
        for file in files:
            if file.startswith('.'):
                continue
            path_to_file = os.path.join(self.path, file)
            size = default_storage.size(path_to_file)
            self.files.append((file, size))

        if sort == 'name':
            self.subdirectories.sort(
                key=lambda subdirectory: subdirectory[0].lower(), reverse=reverse)

            self.files.sort(key=lambda file: file[0].lower(), reverse=reverse)
        else:
            self.subdirectories.sort(
                key=lambda subdirectory: subdirectory[1], reverse=reverse)

            self.files.sort(key=lambda file: file[1], reverse=reverse)

    def iter_subdirectories(self):
        for subdirectory, item_count in self.subdirectories:
            path = encode_url(os.path.join(self.path, subdirectory))
            yield (subdirectory, path, item_count)

    def iter_files(self):
        for file, size in self.files:
            path_to_file = os.path.join(self.path, file)
            file_url = default_storage.url(path_to_file)
            yield (file, file_url, human_readable_size(size))

    def __repr__(self):
        return unicode(self.path) or 'index'

    def is_empty(self):
        return not self.subdirectories and not self.files


# from http://stackoverflow.com/a/1094933
def human_readable_size(num):
    for x in ['Byte','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def encode_url(url):
    return urllib.quote(url.encode('utf-8'))


# from SimpleHTTPRequestHandler
def guess_type(path):
    """Guess the type of a file.

    Argument is a PATH (a filename).

    Return value is a string of the form type/subtype,
    usable for a MIME Content-type header.

    The default implementation looks the file's extension
    up in the table self.extensions_map, using application/octet-stream
    as a default; however it would be permissible (if
    slow) to look inside the data to make a better guess.

    """

    base, ext = os.path.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']

# -*- coding: utf-8 -*-
import os
import urllib
import mimetypes

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
            subdirectory_url = reverse('fileserver_directory', args=[
               encode_url(os.path.join(self.path, subdirectory))])
            yield (subdirectory, subdirectory_url, item_count)

    def iter_files(self):
        for file in self.files:
            if file.startswith('.'):
                continue
            path_to_file = os.path.join(self.path, file)
            size = default_storage.size(path_to_file)
            file_url = default_storage.url(path_to_file)
            yield (file, file_url, human_readable_size(size))

    def __repr__(self):
        return unicode(self.path)


def save_file(path, file):
    # TODO normalize filename
    name = os.path.join(path, file.name)
    default_storage.save(name, file)


# from http://stackoverflow.com/a/1094933
def human_readable_size(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
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

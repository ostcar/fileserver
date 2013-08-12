# Use an inmemory storage
import django.core.files.storage
from ..utils.test import FakeMemoryStorage
default_storage = FakeMemoryStorage()
django.core.files.storage.default_storage = default_storage

from .utils import *
from .views import *

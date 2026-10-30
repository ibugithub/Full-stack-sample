"""Isolated test configuration: never connect to the configured application database."""
import os
from unittest.mock import patch

with patch.dict(os.environ, {'DATABASE_ENGINE': 'sqlite', 'ADMIN_URL': 'admin/'}):
    from .settings import *  # noqa: F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
# Ordinary account tests do not share rate counters. Dedicated throttle tests
# override this alias with a real cache and clear it between test cases.
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    'auth_throttles': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
}

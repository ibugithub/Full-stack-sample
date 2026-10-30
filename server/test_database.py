from unittest import TestCase

from django.core.exceptions import ImproperlyConfigured

from pathlib import Path

from .database import database_configuration, parse_database_url


class DatabaseURLTests(TestCase):
    def test_numeric_port_is_preserved(self):
        config = parse_database_url('postgresql://example:fake-secret@localhost:6543/template')
        self.assertEqual(config['PORT'], 6543)
        self.assertEqual(config['OPTIONS']['sslmode'], 'require')

    def test_missing_port_uses_driver_default(self):
        config = parse_database_url('postgresql://example:fake-secret@localhost/template')
        self.assertEqual(config['PORT'], '')

    def test_percent_encoded_password_is_decoded(self):
        config = parse_database_url('postgresql://example:fake%40secret%23@localhost:5432/template')
        self.assertEqual(config['PASSWORD'], 'fake@secret#')

    def test_invalid_port_is_reported_without_credentials(self):
        with self.assertRaises(ImproperlyConfigured) as caught:
            parse_database_url('postgresql://example:fake-secret@localhost:zXC/template')
        self.assertIn('numeric port', str(caught.exception))
        self.assertNotIn('fake-secret', str(caught.exception))

    def test_unsupported_scheme_is_reported_without_credentials(self):
        with self.assertRaises(ImproperlyConfigured) as caught:
            parse_database_url('unknown://example:fake-secret@localhost/template')
        self.assertNotIn('fake-secret', str(caught.exception))


class DatabaseSwitchTests(TestCase):
    def test_sqlite_ignores_an_invalid_postgresql_url(self):
        config = database_configuration('sqlite', 'postgresql://example:fake@localhost:zXC/template', Path.cwd())
        self.assertEqual(config['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(config['NAME'], Path.cwd() / 'db.sqlite3')

    def test_postgresql_keeps_ssl_and_pooling(self):
        config = database_configuration('postgresql', 'postgresql://example:fake@localhost:5432/template', Path.cwd())
        self.assertEqual(config['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(config['OPTIONS']['sslmode'], 'require')
        self.assertEqual(config['OPTIONS']['pool']['max_size'], 4)
        self.assertTrue(config['CONN_HEALTH_CHECKS'])

    def test_postgresql_requires_a_url(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'DATABASE_URL is required'):
            database_configuration('postgresql', '', Path.cwd())

    def test_invalid_switch_is_rejected(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'DATABASE_ENGINE must be'):
            database_configuration('unknown', '', Path.cwd())

    def test_postgresql_rejects_a_sqlite_url(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'requires a PostgreSQL'):
            database_configuration('postgresql', 'sqlite:///db.sqlite3', Path.cwd())

    def test_unset_switch_preserves_legacy_database_selection(self):
        self.assertEqual(database_configuration(None, '', Path.cwd())['ENGINE'], 'django.db.backends.sqlite3')
        config = database_configuration(None, 'postgresql://example:fake@localhost/template', Path.cwd())
        self.assertEqual(config['ENGINE'], 'django.db.backends.postgresql')

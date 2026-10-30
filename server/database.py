"""Database URL parsing with configuration errors that never reveal credentials."""

import dj_database_url
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


def parse_database_url(url):
    try:
        return dj_database_url.parse(url, conn_max_age=0, ssl_require=True)
    except (ValueError, KeyError):
        raise ImproperlyConfigured(
            'DATABASE_URL is invalid. Use a valid PostgreSQL connection URL with a '
            'numeric port (usually 5432), and percent-encode reserved characters '
            'in the username/password. Leave DATABASE_URL empty only if you intend '
            'to use the local SQLite database. Check both .env and shell variables; '
            'shell variables take precedence.'
        ) from None


def database_configuration(engine, url, base_dir):
    # Preserve existing deployments that have DATABASE_URL but no explicit switch.
    engine = (engine or ('postgresql' if url else 'sqlite')).strip().lower()
    if engine == 'sqlite':
        return {'ENGINE': 'django.db.backends.sqlite3', 'NAME': Path(base_dir) / 'db.sqlite3'}
    if engine != 'postgresql':
        raise ImproperlyConfigured('DATABASE_ENGINE must be sqlite or postgresql.')
    if not url:
        raise ImproperlyConfigured('DATABASE_URL is required when DATABASE_ENGINE=postgresql.')
    config = parse_database_url(url)
    if config['ENGINE'] != 'django.db.backends.postgresql':
        raise ImproperlyConfigured('DATABASE_ENGINE=postgresql requires a PostgreSQL DATABASE_URL.')
    config['OPTIONS']['pool'] = {'min_size': 1, 'max_size': 4, 'timeout': 30}
    config['CONN_HEALTH_CHECKS'] = True
    return config

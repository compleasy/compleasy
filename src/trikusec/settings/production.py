"""
Production-specific settings for TrikuSec.

These settings are used when DJANGO_ENV=production.
"""
from .base import *  # noqa
import os

# Production-specific settings
DEBUG = False

# Require explicit ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError('DJANGO_ALLOWED_HOSTS must be set in production')

# Strict security settings
#SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
#SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
#SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('true', '1', 'yes')
#SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'True').lower() in ('true', '1', 'yes')
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True

# Production logging (INFO level)
LOGGING['root']['level'] = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')

# Database recommendation for production
# SQLite is allowed by default for easier installation, but PostgreSQL is strongly recommended
# for production deployments. See README.md for PostgreSQL setup instructions.
if not os.environ.get('DATABASE_URL'):
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        'DATABASE_URL is not set. Using SQLite by default. '
        'PostgreSQL is strongly recommended for production deployments. '
        'See README.md for setup instructions.'
    )

DATABASES = apply_test_db_override(DATABASES)


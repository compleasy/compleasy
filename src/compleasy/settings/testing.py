"""
Testing-specific settings for Compleasy.

These settings are used when DJANGO_ENV=testing.
"""
from .development import *  # noqa

# Testing-specific settings
# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable rate limiting in tests
RATELIMIT_ENABLE = False

# Simpler password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


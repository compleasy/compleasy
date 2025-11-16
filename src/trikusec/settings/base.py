"""
Base Django settings for trikusec project.

This file contains all common settings shared across all environments.
Environment-specific settings should be in development.py, production.py, or testing.py.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Logging
# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'audit': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'audit.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'audit',
        },
    },
    'loggers': {
        'audit': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        'SECRET_KEY environment variable is not set. '
        'Please set it in your environment or docker compose configuration file. '
        'Generate a secure key using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
    )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'api',
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.AuditLoggingMiddleware',  # Add audit logging
]

ROOT_URLCONF = 'trikusec.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'frontend/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'trikusec.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Support both SQLite (development) and PostgreSQL (production)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL configuration from DATABASE_URL
    # Format: postgresql://user:password@host:port/dbname
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': match.group(5),
                'USER': match.group(1),
                'PASSWORD': match.group(2),
                'HOST': match.group(3),
                'PORT': match.group(4),
                'CONN_MAX_AGE': 600,
                'OPTIONS': {
                    'connect_timeout': 10,
                }
            }
        }
    else:
        raise ValueError('Invalid DATABASE_URL format. Expected: postgresql://user:password@host:port/dbname')
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'trikusec.sqlite3',
        }
    }


def apply_test_db_override(databases):
    """Allow tests to share a database file with a running server when needed."""
    test_db_name = os.environ.get('DJANGO_TEST_DB_NAME')
    if test_db_name:
        databases['default']['TEST'] = {
            'NAME': test_db_name,
        }
    return databases


DATABASES = apply_test_db_override(DATABASES)

# Cache configuration for rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ratelimit-cache',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# STATIC_ROOT: Directory where collectstatic will collect static files for production
# This is required for production deployments with a separate web server (Nginx, Apache)
STATIC_ROOT = os.environ.get('STATIC_ROOT', str(BASE_DIR / 'staticfiles'))

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:3000'
]

if os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS'):
    CSRF_TRUSTED_ORIGINS += os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS').split(',')

# Login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Media files
MEDIA_ROOT = BASE_DIR / 'frontend/media'
MEDIA_URL = '/media/'

# Static files
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/static',
]

# Honor reverse proxy headers for scheme/host when behind Nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security Headers (base settings, overridden in production)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Rate limiting configuration
RATELIMIT_ENABLE = os.environ.get('RATELIMIT_ENABLE', 'True').lower() in ('true', '1', 'yes')
RATELIMIT_USE_CACHE = 'default'

# TrikuSec configuration
TRIKUSEC_URL = os.environ.get('TRIKUSEC_URL', 'https://localhost:443')
# Lynis API URL - falls back to TRIKUSEC_URL if not set
TRIKUSEC_LYNIS_API_URL = os.environ.get('TRIKUSEC_LYNIS_API_URL', TRIKUSEC_URL)


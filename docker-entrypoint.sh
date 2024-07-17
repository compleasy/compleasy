#!/usr/bin/env bash

set -e

COMPLEASY_ADMIN_USERNAME=${COMPLEASY_ADMIN_USERNAME:-admin}
COMPLEASY_ADMIN_EMAIL=${COMPLEASY_ADMIN_EMAIL:-empty@domain.com}
COMPLEASY_ADMIN_PASSWORD=${COMPLEASY_ADMIN_PASSWORD:-admin}
COMPLEASY_URL=${COMPLEASY_URL:-https://localhost:3000}

DJANGO_SUPERUSER_PASSWORD=${COMPLEASY_ADMIN_PASSWORD}
DJANGO_ALLOWED_HOSTS=${COMPLEASY_ALLOWED_HOSTS:-*}
DJANGO_CSRF_TRUSTED_ORIGINS=${COMPLEASY_CSRF_TRUSTED_ORIGINS:-https://localhost:3000}


# Show database migrations
python manage.py showmigrations

# Apply database migrations
python manage.py migrate

# Create admin user (ignore errors)
python manage.py createsuperuser --noinput --username=${COMPLEASY_ADMIN_USERNAME} --email=${COMPLEASY_ADMIN_EMAIL} || true

# Update admin user password (from environment variable)
python manage.py change_admin_password

# Add a random licensekey
python manage.py populate_db_licensekey

# Start server
exec "$@"
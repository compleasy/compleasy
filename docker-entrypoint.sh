#!/usr/bin/env bash

set -e

# COMPLEASY_USERNAME
COMPLEASY_ADMIN_USERNAME=${COMPLEASY_ADMIN_USERNAME:-admin}
# COMPLEASY_PASSWORD
COMPLEASY_ADMIN_PASSWORD=${COMPLEASY_ADMIN_PASSWORD:-admin}
DJANGO_SUPERUSER_PASSWORD=${COMPLEASY_ADMIN_PASSWORD}

# Apply database migrations
python manage.py makemigrations

# Create admin user (ignore errors)
python manage.py createsuperuser --noinput --username=admin || true

# Update admin user password (from environment variable)
python manage.py change_admin_password

# Add a random licensekey
python manage.py populate_db_licensekey

# Start server
python manage.py runserver 0.0.0.0:${COMPLEASY_PORT:-8000}
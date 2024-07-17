#!/usr/bin/env bash

set -e

# COMPLEASY_USERNAME
COMPLEASY_ADMIN_USERNAME=${COMPLEASY_USERNAME:-admin}
# COMPLEASY_PASSWORD
COMPLEASY_ADMIN_PASSWORD=${COMPLEASY_PASSWORD:-admin}
DJANGO_SUPERUSER_PASSWORD=${COMPLEASY_PASSWORD}

# Apply database migrations
python manage.py makemigrations

# Create admin user
python manage.py createsuperuser --noinput --username=admin

# Add a random licensekey
python manage.py populate_db_licensekey

# Start server
python manage.py runserver 0.0.0.0:${COMPLEASY_PORT:-8000}
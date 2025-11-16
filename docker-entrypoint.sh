#!/usr/bin/env bash

set -e

TRIKUSEC_ADMIN_USERNAME=${TRIKUSEC_ADMIN_USERNAME:-admin}
TRIKUSEC_ADMIN_EMAIL=${TRIKUSEC_ADMIN_EMAIL:-empty@domain.com}
TRIKUSEC_ADMIN_PASSWORD=${TRIKUSEC_ADMIN_PASSWORD:-admin}
TRIKUSEC_URL=${TRIKUSEC_URL:-https://localhost:443}
TRIKUSEC_CSRF_TRUSTED_ORIGINS=${TRIKUSEC_URL:-https://localhost:443}

DJANGO_SUPERUSER_PASSWORD=${TRIKUSEC_ADMIN_PASSWORD}
DJANGO_ALLOWED_HOSTS=${TRIKUSEC_ALLOWED_HOSTS:-*}
DJANGO_CSRF_TRUSTED_ORIGINS=${TRIKUSEC_CSRF_TRUSTED_ORIGINS:-https://localhost:443}

# Export Django environment variables
export DJANGO_SUPERUSER_PASSWORD
export DJANGO_ALLOWED_HOSTS
export DJANGO_CSRF_TRUSTED_ORIGINS

# Show database migrations
python manage.py showmigrations

# Apply database migrations
python manage.py migrate

# Create admin user (ignore errors)
python manage.py createsuperuser --noinput --username=${TRIKUSEC_ADMIN_USERNAME} --email=${TRIKUSEC_ADMIN_EMAIL} || true

# Update admin user password (from environment variable)
# Allow this to fail without crashing the container
python manage.py change_admin_password || true

# Add a license key (use provided env var if available, otherwise generate)
# Allow this to fail without crashing the container
if [ -n "${TRIKUSEC_LICENSE_KEY}" ]; then
  python manage.py populate_db_licensekey "${TRIKUSEC_LICENSE_KEY}" || true
else
  python manage.py populate_db_licensekey || true
fi

# Start server
exec "$@"
#!/usr/bin/env bash

set -e

# Set environment variables
export SECRET_KEY=${SECRET_KEY:-test-secret-key-for-testing}
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=*

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Run the command passed to the container
exec "$@"


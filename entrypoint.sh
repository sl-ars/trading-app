#!/bin/sh

echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started."

# Run migrations
poetry run python manage.py migrate --noinput

# Collect static files
poetry run python manage.py collectstatic --noinput

# Start Gunicorn server
exec poetry run gunicorn trading_app.wsgi:application --bind 0.0.0.0:8000
#!/bin/sh

echo "Waiting for PostgreSQL to start..."
while ! timeout 1 bash -c 'cat < /dev/null > /dev/tcp/db/5432'; do
  sleep 1
done
echo "PostgreSQL started."

if [ "$RUN_CELERY" = "true" ]; then
  echo "Starting Celery Worker..."
  exec poetry run celery -A trading_app worker -l info -P solo --logfile=/dev/stdout --without-gossip --without-mingle --without-heartbeat
else
  # Collect static files
  echo "Collecting static files..."
  poetry run python manage.py collectstatic --noinput

  # Run database migrations
  echo "Applying database migrations..."
  poetry run python manage.py migrate --noinput

  # Start Daphne in the background
  echo "Starting Daphne..."
  poetry run daphne -b 0.0.0.0 -p 8001 trading_app.asgi:application &

  # Start Gunicorn in the foreground
  echo "Starting Gunicorn..."
  exec poetry run gunicorn trading_app.wsgi:application --bind 0.0.0.0:8000
fi
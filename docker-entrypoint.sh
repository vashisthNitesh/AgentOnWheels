#!/bin/sh
set -e

echo "==> Starting AgentOnWheels application..."

# Apply database migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "==> Applying database migrations..."
  python manage.py migrate --noinput || echo "==> Migrations skipped or failed, continuing..."
fi

# Determine port (Render automatically provides $PORT)
LISTEN_PORT="${PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-4}"

echo "==> Starting Gunicorn on port $LISTEN_PORT (workers: $WORKERS, threads: $THREADS)..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:$LISTEN_PORT" \
  --workers "$WORKERS" \
  --threads "$THREADS" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

#!/bin/sh
set -e

echo "==> Starting Axle TMS application..."

# Apply database migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "==> Applying database migrations..."
  python manage.py migrate --noinput || echo "==> Migrations skipped or failed, continuing..."
fi

# Optional auto-seed demo data
if [ "$SEED_DEMO" = "1" ]; then
  echo "==> Checking and seeding demo dataset..."
  python manage.py seed_demo || echo "==> Seeding skipped or failed, continuing..."
fi

# Ensure admin superuser exists
if [ -n "$DJANGO_ADMIN_PASSWORD" ] || [ "$CREATE_ADMIN" = "1" ]; then
  echo "==> Ensuring admin user exists..."
  python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth.models import User
pwd = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin')
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@axletms.com', pwd)
    print('Created superuser: admin')
else:
    u = User.objects.get(username='admin')
    u.set_password(pwd)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Verified superuser: admin')
" || echo "==> Superuser creation skipped, continuing..."
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

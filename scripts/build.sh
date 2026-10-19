#!/usr/bin/env bash
# Build the Vue app into Django (single server).
set -euo pipefail
cd "$(dirname "$0")/.."
(cd frontend && npm install && npm run build)
mkdir -p templates && cp frontend/dist/index.html templates/index.html
if [ -f ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="$(command -v python || command -v python3)"
fi
"$PY" manage.py collectstatic --noinput -v0
echo "Built. Run: gunicorn config.wsgi -b 0.0.0.0:8000  (or python manage.py runserver)"
